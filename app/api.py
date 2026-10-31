""" Aplicação para o módulo de extensão DevOps """

from datetime import datetime, timezone
from typing import Annotated, List

from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, select
import requests
from requests.exceptions import ConnectionError as RequestConnectionError

from app.modelo import Tarefa

ENGINE = create_engine("sqlite:///banco.db", connect_args={'check_same_thread': False})

def criar_sessao():
    with Session(ENGINE) as s:
        yield s

SESSAO = Annotated[Session, Depends(criar_sessao)]

async def inicializacao(api: FastAPI):
    print("Antes de inicializar a API")
    SQLModel.metadata.create_all(ENGINE)
    yield
    print("Finalizando")

APP = FastAPI(lifespan=inicializacao)
TAREFAS = []



# GET /tarefas: Lista todas as tarefas (somente id e titulo)
@APP.get("/tarefas")
async def tarefas(sessao: SESSAO) -> List[Tarefa]:
    """ Rota para listar as tarefas. """
    lista_tarefas = sessao.exec(select(Tarefa).offset(0)).all()

    return lista_tarefas

# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(sessao: SESSAO, titulo: str, descricao: str = None):
    """ Rota para criar uma tarefa. """
    tarefa_nova = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now().astimezone(timezone.utc),
    )

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    return {"mensagem": "OK"}

async def tarefa_especifica(sessao: SESSAO, id_tarefa: int) -> Tarefa:
    """Rota para visualizar uma tarefa específica"""
    # select * from tarefas where id == id_tarefa
    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if resultado:
        if resultado[0].id is None:
            return {"mensagem":" Tarefa nao existe"}

        return resultado[0]

    return {"mensagem": "Tarefa não existe"}

# PUT /tarefas/{id}: Atualiza tarefa específica
@APP.put("/tarefas/{id_tarefa}")
async def concluir_tarefa(id_tarefa: int, sessao: SESSAO):
    """ Rota para concluir uma tarefa. """

    # Atualizar a rota para suportar o SQLModel/Conexão com BD
    # Usar select para filtrar as tarefas com base no ID e se estiver concluída
    # Atualizar usando sessao.add, sessao.commit, sessao.refresh

    regra = select(Tarefa).where(Tarefa.id == id_tarefa, Tarefa.concluida.is_(False),)
    tarefa = sessao.exec(regra).first()

    if tarefa is None:
        return {"mensagem": "Tarefa não existe"}

    tarefa.finalizar()
    sessao.add(tarefa)
    sessao.commit()
    sessao.refresh(tarefa)

    try:
        requests.post(
            f"http://localhost:8000/notificar?id={id_tarefa}&titulo={tarefa.titulo}",
            timeout=1,
        )
    except RequestConnectionError as e:
        print(e)

    return {"mensagem": "Tarefa atualizada"}

# DELETE /tarefas/{id_tarefa}: Exclui tarefa
@APP.delete("/tarefas/{id_tarefa}")
async def apagar_tarefa(sessao: SESSAO, id_tarefa: int):
    """ Rota para apagar tarefa. """
    # 1. Selecionar a tarefa de ID recebido como parâmetro
    # 2. Remover tarefa da lista de tarefas
    # 3. Caso a tarefa não exista, você tem que mostrar que a tarefa não existe
   
    # Atualizar a rota para suportar o SQLModel/Conexão com BD
    # Usar select para filtrar as tarefas com base no ID 
    # Apagar tarefa com base no id (session.delete)
    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()
    
    if not resultado:
        return {"mensagem": "Tarefa não existe"}    

    tarefa = resultado[0]

    sessao.delete(tarefa)
    sessao.commit()

    return {"mensagem": "Tarefa removida"}

@APP.get("/")
async def index():
    """ Rota raíz. """
    return {"mensagem": "Olá, mundo!"}


# 1. Implementar uma rota chamada "/autor" que retorna
# um dicionário no formato {"mensagem": SEU NOME COMPLETO}
@APP.get("/autor")
async def autor():
    """ Rota para retornar o autor da aplicação """
    return {"mensagem": "Thionas Nascimento"}

# 2. Criar um teste unitário para verificar se a rota
# está produzindo o resultado esperado

# 3. Verificar se o código está no padrão do PyLint

# 4. Enviar o código para o repositório (git push)
