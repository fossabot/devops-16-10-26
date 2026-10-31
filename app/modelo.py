""" Modelos da aplicação de tarefas """

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class Tarefa(SQLModel, table= True):
    """ Modelo de tarefa"""
    id: int = Field(alias="_id", primary_key=True, unique=True, default=None)
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
        self.data_conclusao = datetime.now(timezone.utc).replace(microsecond=0)
