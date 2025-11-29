from django.test.runner import DiscoverRunner

class NoDbTestRunner(DiscoverRunner):
    """
    Test runner que NO crea, NO migra y NO destruye la base de datos.
    Usa la BD ya existente en TEST.NAME.
    """
    def setup_databases(self, **kwargs):
        # No crear, no migrar
        return None

    def teardown_databases(self, old_config, **kwargs):
        # No borrar la BD al finalizar
        pass
