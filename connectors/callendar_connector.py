from config import Config


class Callendar(Config):
    def get_connection(self):
        pass

    def do(self):
        self.get_connection()
        import pdb; pdb.set_trace()
