#Họ và Tên: Nguyễn Đức Hưng
#MSSV:202418913
from datetime import date
from decimal import Decimal

from models import *


def print_slip(slip, as_of):
    print(f"Phiếu {slip.slip_id} | {slip.borrower.full_name} | phòng {slip.teaching_room}")
    for item in slip.items:
        trang_thai = f"đã trả {item.returned_date}" if item.is_returned() else "chưa trả"
        print(f"  - {item.device.name}: hạn {item.due_date}, {trang_thai}, "
              f"trễ {item.get_late_days(as_of)} ngày, phí {item.calculate_late_fee(as_of)}")
def success_flow():
    print("=== 11.1 LUỒNG THÀNH CÔNG ===")
    gv = Lecturer("GV01", "Nguyễn Văn A")

    pj = ProjectorRemote("PJ01", "Điều khiển máy chiếu", 2022, Decimal("200000"), "Epson")
    ac = AirConditionerRemote("AC01", "Điều khiển điều hòa", 2018, Decimal("300000"), "Daikin")
    mic = Microphone("MIC01", "Micro không dây", 2020, Decimal("500000"), True)
    room = ClassRoom("B204", "Phòng B204", 40)
    for d in (pj, ac, mic):
        room.add_device(d)

    slip = BorrowingSlip("PM01", gv, "B204", date(2026, 10, 1))
    slip.add_device(pj, 1)
    slip.add_device(mic, 1)
    slip.add_device(ac, 2)  # điều hòa không trả để có một thiết bị chưa trả
    print("Trả máy chiếu, phí:", slip.return_device("PJ01", date(2026, 10, 2)))
    print("Trả micro, phí:", slip.return_device("MIC01", date(2026, 10, 4)))

    as_of = date(2026, 10, 5)
    print_slip(slip, as_of)
    print("Số item trả muộn:", len(slip.get_late_items(as_of)))
    print("Số item chưa trả:", len(slip.get_unreturned_items()))
    print("Tổng phí trễ:", slip.calculate_total_late_fee(as_of))
    print("Chi phí bảo trì của phòng:", room.calculate_annual_maintenance_cost())
    for d in room.get_devices_requiring_maintenance():
        print("Cần bảo trì:", d.name)   
def exception_flow():
    print("\n=== 11.2 LUỒNG NGOẠI LỆ ===")
    gv = Lecturer("GV01", "Nguyễn Văn A")
    ta = TeachingAssistant("TA01", "Trần Thị B")
    day = date(2026, 10, 1)

    # 1. Mượn điều hòa đang bảo trì
    ac = AirConditionerRemote("AC01", "Điều khiển điều hòa", 2018, Decimal("300000"), "Daikin")
    ac.mark_as_under_maintenance()
    slip = BorrowingSlip("PM02", gv, "B204", day)
    try:
        slip.add_device(ac, 1)
    except DeviceUnavailableException as e:
        print("1.", e)
    finally:
        print(f"   -> {ac.device_id}: {ac.status.name}, số item trong phiếu: {len(slip.items)}")

    # 2. Trợ giảng mượn thiết bị thứ ba
    slip = BorrowingSlip("PM03", ta, "B204", day)
    m1 = Microphone("M1", "Micro 1", 2020, Decimal("100000"), True)
    m2 = Microphone("M2", "Micro 2", 2020, Decimal("100000"), True)
    m3 = Microphone("M3", "Micro 3", 2020, Decimal("100000"), True)
    slip.add_device(m1, 1)
    slip.add_device(m2, 1)
    try:
        slip.add_device(m3, 1)
    except BorrowLimitExceededException as e:
        print("2.", e)
    finally:
        print(f"   -> {m3.device_id}: {m3.status.name}, số item trong phiếu: {len(slip.items)}")

    # 3. Thêm một micro hai lần
    mic = Microphone("MIC01", "Micro", 2020, Decimal("500000"), True)
    slip = BorrowingSlip("PM04", gv, "B204", day)
    slip.add_device(mic, 1)
    try:
        slip.add_device(mic, 1)
    except DuplicateDeviceException as e:
        print("3.", e)
    finally:
        print(f"   -> {mic.device_id}: {mic.status.name}, số item trong phiếu: {len(slip.items)}")

    # 4. Mượn micro 3 ngày (tối đa 1 ngày)
    mic = Microphone("MIC02", "Micro", 2020, Decimal("500000"), True)
    slip = BorrowingSlip("PM05", gv, "B204", day)
    try:
        slip.add_device(mic, 3)
    except InvalidBorrowPeriodException as e:
        print("4.", e)
    finally:
        print(f"   -> {mic.device_id}: {mic.status.name}, số item trong phiếu: {len(slip.items)}")

    # 5. Trả máy chiếu có thật nhưng không thuộc phiếu
    pj = ProjectorRemote("PJ01", "Điều khiển máy chiếu", 2022, Decimal("200000"), "Epson")
    mic = Microphone("MIC05", "Micro", 2020, Decimal("500000"), True)
    slip = BorrowingSlip("PM06", gv, "B204", day)
    slip.add_device(mic, 1)
    try:
        slip.return_device(pj.device_id, day)
    except DeviceNotInSlipException as e:
        print("5.", e)
    finally:
        print(f"   -> {mic.device_id}: {mic.status.name}, {pj.device_id}: {pj.status.name}, "
              f"số item trong phiếu: {len(slip.items)}")

    # 6. Trả một thiết bị hai lần
    mic = Microphone("MIC03", "Micro", 2020, Decimal("500000"), True)
    slip = BorrowingSlip("PM07", gv, "B204", day)
    slip.add_device(mic, 1)
    slip.return_device("MIC03", day)
    try:
        slip.return_device("MIC03", day)
    except DeviceAlreadyReturnedException as e:
        print("6.", e)
    finally:
        item = slip.items[0]
        print(f"   -> {mic.device_id}: {mic.status.name}, ngày trả vẫn là {item.returned_date}, "
              f"số item trong phiếu: {len(slip.items)}")

    # 7. Ngày trả trước ngày mượn
    mic = Microphone("MIC04", "Micro", 2020, Decimal("500000"), True)
    slip = BorrowingSlip("PM08", gv, "B204", day)
    slip.add_device(mic, 1)
    try:
        slip.return_device("MIC04", date(2026, 9, 30))
    except InvalidReturnDateException as e:
        print("7.", e)
    finally:
        item = slip.items[0]
        print(f"   -> {mic.device_id}: {mic.status.name}, đã trả: {item.is_returned()}, "
              f"số item trong phiếu: {len(slip.items)}")


if __name__ == "__main__":
    success_flow()
    exception_flow()
