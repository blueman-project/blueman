from blueman.bluez.obex.Base import Base


class Session(Base):
    _interface_name = 'org.bluez.obex.Session1'

    def __init__(self, obj_path: str):
        super().__init__(obj_path=obj_path)

    @property
    def address(self) -> str:
        dest: str = self.get('Destination')
        return dest

    @property
    def root(self) -> str:
        root: str = self.get('Root')
        return root
