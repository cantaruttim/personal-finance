import os
from datetime import datetime
from pathlib import Path

class Revenue:

    def __init__(self, owner: str, month: int, year: int, value: float):
        self.owner = owner.strip()
        self.month = month
        self.year = year
        self.value = value

        self._validate()

    # =============================
    # Validações
    # =============================
    def _validate(self):
        if not isinstance(self.owner, str) or not self.owner:
            raise ValueError("Owner deve ser uma string não vazia.")

        if not isinstance(self.month, int) or not (1 <= self.month <= 12):
            raise ValueError("Month deve ser um inteiro entre 1 e 12.")

        if not isinstance(self.year, int) or self.year < 1900:
            raise ValueError("Year inválido.")

        if not isinstance(self.value, (int, float)) or self.value < 0:
            raise ValueError("Value deve ser numérico e positivo.")

    # =============================
    # Propriedade ANOMES (útil pra gráfico depois)
    # =============================
    @property
    def anomes(self) -> str:
        return f"{str(self.month).zfill(2)}{self.year}"

    # =============================
    # Serialização
    # =============================
    def to_csv_line(self) -> str:
        return f"{self.owner},{self.month:02d},{self.year},{self.value:.2f},{self.anomes}\n"

    # =============================
    # Persistência
    # =============================

    def save(self, filepath: str = "./data/revenues.txt"):
        path = Path(filepath)

        try:
            # Cria diretórios automaticamente se não existirem
            path.parent.mkdir(parents=True, exist_ok=True)

            file_exists = path.exists()

            with path.open("a", encoding="utf-8") as file:

                # Se o arquivo não existir, cria cabeçalho
                if not file_exists:
                    file.write("owner,month,year,value,anomes\n")

                file.write(self.to_csv_line())

        except Exception as e:
            raise IOError(f"Erro ao salvar arquivo: {e}")
    
    # =============================
    # Representação
    # =============================
    def __repr__(self):
        return (
            f"Revenue(owner='{self.owner}', "
            f"month={self.month}, "
            f"year={self.year}, "
            f"value={self.value:.2f})"
        )