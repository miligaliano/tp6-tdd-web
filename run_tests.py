import pytest


class TestReporter:
    """
    Plugin de pytest para capturar los resultados de cada test.
    """

    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            if report.passed:
                self.passed.append(report.nodeid)
            elif report.failed:
                self.failed.append(report.nodeid)
            elif report.skipped:
                self.skipped.append(report.nodeid)


def run_and_report():
    reporter = TestReporter()

    pytest.main(["-q", "test_comprar_entradas.py"], plugins=[reporter])

    print("\n🧪 RESULTADOS DE LOS TESTS DE COMPRA DE ENTRADAS")
    print("──────────────────────────────────────────────")

    if reporter.passed:
        for test in reporter.passed:
            nombre = test.split("::")[-1].replace("test_", "")
            print(f"✅ {nombre} pasó correctamente")
    else:
        print(
            "❌ No se detectaron tests pasados. Revisa los nombres o errores de ejecución.")

    if reporter.failed:
        print("\n🚨 Tests con errores:")
        for test in reporter.failed:
            nombre = test.split("::")[-1]
            print(f"   - {nombre}")

    print("\nTotal de tests pasados:", len(reporter.passed))
    print("──────────────────────────────────────────────")


if __name__ == "__main__":
    run_and_report()
