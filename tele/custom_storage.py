from aiogram.contrib.fsm_storage.memory import MemoryStorage

class CustomMemoryStorage(MemoryStorage):
    def _cleanup(self, chat, user):
        if chat in self.data and user in self.data[chat]:
            if self.data[chat][user] == {'state': None, 'data': {}, 'bucket': {}}:
                del self.data[chat][user]
            if not self.data[chat]:
                del self.data[chat]
