#Họ và Tên: Nguyễn Đức Hưng
#MSSV:202418913
from enum import Enum
from abc import ABC,abstractmethod
from datetime import date, timedelta
from decimal import Decimal
LATE_FEE_PER_DAY=Decimal("10000") #Giả định phí muộn/ngày là 10000
#Lớp trạng thái thiết bị
class DeviceStatus(Enum):
    AVAILABLE="Available"
    BORROWED='Borrowed'
    UNDER_MAINTENANCE="Under_Maintenance"
    RETIRED="Retired" 
class BorrowingException(Exception):
    def __init__(self,message):
        super().__init__(message)
class DeviceUnavailableException(BorrowingException):
    def __init__(self,device_id: str, current_status: DeviceStatus):
        self.device_id=device_id
        self.current_status=current_status
        super().__init__(
            f"Thiết bị {device_id} không sẵn sàng "
            f"(trạng thái: {current_status.name})"
        )
class BorrowLimitExceededException(BorrowingException):
    def __init__(self, borrower_id, maximum_devices):
        self.borrower_id=borrower_id
        self.maximum_devices=maximum_devices
        super().__init__(
            f"Người mượn {borrower_id} đã đạt tối đa {maximum_devices} thiết bị"
        )
class InvalidBorrowPeriodException(BorrowingException):
    def __init__ (self, device_id, requested, maximum):
        self.device_id=device_id
        self.requested=requested
        self.maximum=maximum
        super().__init__(
            f"Thiết bị {device_id}: yêu cầu {requested}, tối đa {maximum}"
        )
class DuplicateDeviceException(BorrowingException):
    def __init__(self,device_id):
        self.device_id=device_id
        super().__init__(
            f'Thiết bị {device_id} đã có trong phiếu'
        )
class DeviceNotInSlipException(BorrowingException):
    def __init__(self,device_id,slip_id):
        self.device_id=device_id
        self.slip_id=slip_id
        super().__init__(
            f"Thiết bị {device_id} không thuộc phiếu {slip_id}"
        )
class DeviceAlreadyReturnedException(BorrowingException):
    def __init__(self,device_id,returned_date):
        self.device_id=device_id
        self.returned_date=returned_date
        super().__init__(
            f"Thiết bị {device_id} đã được trả vào {returned_date}"
        )
class InvalidReturnDateException(BorrowingException):
    def __init__(self,borrowed_date,returned_date):
        self.borrowed_date=borrowed_date
        self.returned_date=returned_date
        super().__init__(
            f"Ngày trả trước ngày mượn"
        )
class Device(ABC):
    def __init__(self,device_id,name,year,price,max_borrow_days,max_periods,status=DeviceStatus.AVAILABLE):
        if  not device_id or not device_id.strip():
            raise ValueError(f"Mã thiết bị không được để rỗng")
        self._device_id=device_id
        if not name or not name.strip():
            raise ValueError("Tên thiết bị không được để rỗng")
        self._name=name
        if year > date.today().year:
            raise ValueError(f"Năm không phù hợp")
        self._year=year
        if price <=0:
            raise ValueError(f"Giá mua phải lớn hơn 0")
        self._price=price
        if max_borrow_days <=0:
            raise ValueError("Ngày mượn tối đa phải lớn hơn 0")
        self._max_borrow_days=max_borrow_days
        if max_periods<=0:
            raise ValueError("Số tiết mượn tối đa phải lớn hơn 0")
        self._max_periods=max_periods
        if not isinstance(status,DeviceStatus):
            raise ValueError("Trạng thái không hợp lệ")
        self._status=status
    @property
    def device_id(self):
        return self._device_id
    @property
    def name(self):
        return self._name
    @property
    def year(self):
        return self._year
    @property
    def price(self):
        return self._price
    @property
    def max_borrow_days(self):
        return self._max_borrow_days
    @property
    def max_periods(self):
        return self._max_periods
    @property
    def status(self):
        return self._status
    def get_years_in_use(self):
        S=date.today().year-self.year
        return S
    @abstractmethod
    def calculate_annual_maintenance_cost(self):
        pass
    def mark_as_available(self):
        self._status=DeviceStatus.AVAILABLE
    def mark_as_borrowed(self):
        self._status=DeviceStatus.BORROWED
    def mark_as_under_maintenance(self):
        self._status=DeviceStatus.UNDER_MAINTENANCE
    def mark_as_retired(self):
        self._status=DeviceStatus.RETIRED
    def __str__(self):
        return f"[{self._device_id}] {self._name} ({self._year}) - {self._status.value}"
class Microphone(Device):
    def __init__(self,device_id,name,year,price,is_wireless,status=DeviceStatus.AVAILABLE):
        super().__init__(device_id,name,year,price,max_borrow_days=1,max_periods=5,status=status)
        self._is_wireless=is_wireless
    @property
    def is_wireless(self):
        return self._is_wireless
    def calculate_annual_maintenance_cost(self) -> Decimal:
        rate=Decimal("0.15") if self._is_wireless else Decimal("0.05")
        return self._price*rate
class AirConditionerRemote(Device):
    def __init__(self,device_id,name,year,price,supported_model,status=DeviceStatus.AVAILABLE):
        super().__init__(device_id,name,year,price,max_borrow_days=3,max_periods=5,status=status)
        self._supported_model=supported_model
    @property
    def supported_model(self):
        return self._supported_model
    def calculate_annual_maintenance_cost(self):
        Cost=self._price*Decimal("0.05")+self.get_years_in_use()*10000
        return Cost
class ProjectorRemote(Device):
    def __init__(self,device_id,name,year,price,projector_brand,status=DeviceStatus.AVAILABLE):
        super().__init__(device_id,name,year,price,max_borrow_days=3,max_periods=5,status=status)
        self._projector_brand=projector_brand
    @property
    def projector_brand(self):
        return self._projector_brand
    def calculate_annual_maintenance_cost(self):
        Cost=self._price*Decimal("0.08")
        return Cost
class ClassRoom:
    def __init__(self,room_id,room_name,capacity):
        if not room_id or not room_id.strip(): 
            raise ValueError("Mã phòng không để trống")
        self._room_id=room_id
        if not room_name or not room_name.strip():
            raise ValueError("Tên phòng không để trống")
        self._room_name=room_name
        if   not isinstance(capacity,int) or capacity <=0:
            raise ValueError("Sức chứa phải là 1 số nguyên lớn hơn 0")
        self._capacity=capacity
        self._devices=[]
    @property
    def room_id(self):
        return self._room_id
    @property
    def room_name(self):
        return self._room_name
    @property
    def capacity(self):
        return self._capacity
    @property
    def devices(self):
        return tuple(self._devices)
    def find_device(self,device_id):
        for i in self._devices:
            if i.device_id==device_id:
                return i
        return None
    def add_device(self,device):
        if device is None:
            raise ValueError("Thiết bị không tồn tại")
        if self.find_device(device.device_id) is not None:
            raise DuplicateDeviceException(device.device_id)
        self._devices.append(device)
    def remove_device(self,device_id):
        if device_id is None:
            return False
        device=self.find_device(device_id)
        if device is None:
            return False
        self._devices.remove(device)
        return True
    def calculate_annual_maintenance_cost(self):
        return sum((i.calculate_annual_maintenance_cost() for i in self._devices),Decimal("0"))
    def get_devices_requiring_maintenance(self):
        return[i for i in self._devices if i.status==DeviceStatus.UNDER_MAINTENANCE or i.get_years_in_use()>5]
class IBorrower(ABC):
    @property
    @abstractmethod
    def borrower_id(self):
        pass
    @property
    @abstractmethod
    def full_name(self):
        pass
    @abstractmethod
    def get_maximum_devices(self)->int:
        pass
class Lecturer(IBorrower):
    def __init__(self, borrower_id, full_name):
        if not borrower_id or not borrower_id.strip():
            raise ValueError("Mã người mượn không được để trống")
        if not full_name or not full_name.strip():
            raise ValueError("Họ tên không được để trống")
        self._borrower_id = borrower_id
        self._full_name = full_name
    @property
    def borrower_id(self):
        return self._borrower_id
    @property
    def full_name(self):
        return self._full_name
    def get_maximum_devices(self):
        return 3
class TeachingAssistant(IBorrower):
    def __init__(self, borrower_id, full_name):
        if not borrower_id or not borrower_id.strip():
            raise ValueError("Mã người mượn không được để trống")
        if not full_name or not full_name.strip():
            raise ValueError("Họ tên không được để trống")
        self._borrower_id=borrower_id
        self._full_name=full_name
    @property
    def borrower_id(self):
        return self._borrower_id
    @property
    def full_name(self):
        return self._full_name
    def get_maximum_devices(self):
        return 2
class BorrowItem:
    def __init__(self, device, borrowed_date, due_date, from_period, to_period):
        if device is None:
            raise ValueError("Thiết bị không được để trống")
        if due_date < borrowed_date:
            raise ValueError("Hạn trả phải sau hoặc bằng ngày mượn")
        if from_period < 1 or from_period > to_period:
            raise ValueError("Tiết mượn không hợp lệ")
        self._device=device
        self._borrowed_date=borrowed_date
        self._due_date=due_date
        self._from_period=from_period
        self._to_period=to_period
        self._returned_date=None
    @property
    def device(self):
        return self._device
    @property
    def borrowed_date(self):
        return self._borrowed_date
    @property
    def due_date(self):
        return self._due_date
    @property
    def from_period(self):
        return self._from_period
    @property
    def to_period(self):
        return self._to_period
    @property
    def returned_date(self):
        return self._returned_date
    def is_returned(self):
        return self._returned_date is not None
    def mark_returned(self, returned_date):
        if self.is_returned():
            raise DeviceAlreadyReturnedException(self._device.device_id, self._returned_date)
        if returned_date < self._borrowed_date:
            raise InvalidReturnDateException(self._borrowed_date, returned_date)
        self._returned_date=returned_date  
    def get_late_days(self, as_of):
        end = self._returned_date if self._returned_date is not None else as_of
        return max(0, (end - self._due_date).days)
    def is_late(self, as_of):
        return self.get_late_days(as_of) > 0
    def calculate_late_fee(self, as_of):
        return self.get_late_days(as_of) * LATE_FEE_PER_DAY
class BorrowingSlip:
    def __init__(self, slip_id, borrower, teaching_room, borrowed_date):
        if not slip_id or not slip_id.strip():
            raise ValueError("Mã phiếu không được trống")
        if borrower is None:
            raise ValueError("Người mượn không được rỗng")
        if not teaching_room or not teaching_room.strip():
            raise ValueError("Phòng học không được rỗng")
        self._slip_id = slip_id
        self._borrower = borrower
        self._teaching_room = teaching_room
        self._borrowed_date = borrowed_date
        self._items = []
    @property
    def slip_id(self):
        return self._slip_id
    @property
    def borrower(self):
        return self._borrower
    @property
    def teaching_room(self):
        return self._teaching_room
    @property
    def borrowed_date(self):
        return self._borrowed_date
    @property
    def items(self):
        return tuple(self._items)
    def find_item(self, device_id):
        for i in self._items:
            if i.device.device_id == device_id:
                return i
        return None
    def validate_borrowing(self, device, borrow_days, from_period, to_period):
        if device is None:
            raise ValueError("Thiết bị không được để trống")
        if borrow_days <= 0 or borrow_days > device.max_borrow_days:
            raise InvalidBorrowPeriodException(device.device_id, borrow_days, device.max_borrow_days)
        periods = to_period - from_period + 1
        if periods > device.max_periods:
            raise InvalidBorrowPeriodException(device.device_id, periods, device.max_periods)
        if self.find_item(device.device_id) is not None:
            raise DuplicateDeviceException(device.device_id)
        max_devices = self._borrower.get_maximum_devices()
        if len(self._items) >= max_devices:
            raise BorrowLimitExceededException(self._borrower.borrower_id, max_devices)
        if device.status != DeviceStatus.AVAILABLE:
            raise DeviceUnavailableException(device.device_id, device.status)
    def add_device(self, device, borrow_days, from_period=1, to_period=1):
        self.validate_borrowing(device, borrow_days, from_period, to_period)
        due_date = self._borrowed_date + timedelta(days=borrow_days)
        item = BorrowItem(device, self._borrowed_date, due_date, from_period, to_period)
        device.mark_as_borrowed()
        self._items.append(item)
    def return_device(self, device_id, returned_date):
        if not device_id:
            raise ValueError("device_id không được rỗng")
        i = self.find_item(device_id)
        if i is None:
            raise DeviceNotInSlipException(device_id, self._slip_id)
        i.mark_returned(returned_date)
        i.device.mark_as_available()
        return i.calculate_late_fee(returned_date)
    def calculate_total_late_fee(self, as_of):
        return sum((i.calculate_late_fee(as_of) for i in self._items), Decimal("0"))
    def get_unreturned_items(self):
        return [i for i in self._items if not i.is_returned()]
    def get_late_items(self, as_of):
        return [i for i in self._items if i.is_late(as_of)]


          


        


