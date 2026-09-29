import unittest

import pandas as pd

from src.dashboard_app import apply_filters, calculate_kpis, load_data


class DashboardUtilsTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "ano": [2023, 2023, 2024],
                "senioridade": ["Pleno", "Senior", "Pleno"],
                "contrato": ["CLT", "PJ", "CLT"],
                "tamanho_empresa": ["M", "G", "P"],
                "cargo": ["Analista", "Cientista", "Analista"],
                "usd": [120000, 160000, 140000],
                "remoto": ["Híbrido", "Remoto", "Presencial"],
                "residencia_iso3": ["BRA", "USA", "BRA"],
            }
        )

    def test_apply_filters_keeps_only_matching_records(self):
        filtered = apply_filters(
            self.df,
            anos=[2023],
            senioridades=["Pleno"],
            contratos=["CLT"],
            tamanhos=["M"],
        )

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["cargo"], "Analista")

    def test_calculate_kpis_summarizes_values(self):
        metrics = calculate_kpis(self.df)

        self.assertAlmostEqual(metrics["salario_medio"], 140000)
        self.assertEqual(metrics["total_registros"], 3)
        self.assertEqual(metrics["cargo_mais_frequente"], "Analista")

    def test_load_data_returns_dataframe_from_local_fallback(self):
        df = load_data(csv_path="dados-imersao-final.csv")

        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("usd", df.columns)


if __name__ == "__main__":
    unittest.main()
