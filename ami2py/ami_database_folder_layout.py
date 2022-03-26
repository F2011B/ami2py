import os

ERROR_RETURNED = True


class AmiDbFolderLayout:
    def get_symbol_root_folder(self, symbol):
        if symbol[0] in ["^", "~","@"]:
            return "_"
        return symbol[0].lower()

    def _get_symbol_path(self, root, symbol):
        assert os.path.isdir(root), f"{root} is not a directory"
        if symbol.lower() == "broker.master":
            return os.path.join(root, f"{symbol}")

        symbol_folder = self.get_symbol_root_folder(symbol)
        return os.path.join(root, f"{symbol_folder}/{symbol}")
