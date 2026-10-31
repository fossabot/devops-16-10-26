""" Modelos da aplicação de tarefas """

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Tarefa(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    concluida: bool = False
    data_criacao: datetime = Field(serialization_alias="criada_em")
    data_conclusao: Optional[datetime] = Field(
        default=None,
        serialization_alias="concluida_em",
    )

    def finalizar(self):
        """ Método para finalizar tarefa """
        self.concluida = True
        self.data_conclusao = datetime.now().replace(microsecond=0)
