# Ambiente

## Virtualenv

Criar uma Virtualenv:

```
$ python -m venv venv
```

Iniciar a Virtualenv:

* Para Sistemas baseados em Unix
```
$ source venv/bin/active
```
* Para Windows
```
$ venv/Scripts/activate
```

## Dependências do Projeto

Instalar todas as dependências:

```
$ pip install -r requirements.txt
```

Instalar manualmente as dependências:

```
pip install "fastapi[standard]"
pip install fastapi-versionizer
pip install requests
pip install langchain==0.0.354
pip install langchain-openai==0.0.5
```

## Dockerfile

### Build

Para criar uma imagem no Docker, execute o comando abaixo:

```
docker build -t agent .
```

### Run

Para criar um container no Docker, execute o comando abaixo:

```
docker run --name agent --env-file .env.docker -p 5002:5002 agent
```

### Test

Para testar a API executando no Docker, basta acessar o link abaixo:

http://localhost:5001/api/latest/docs