# SFG Catalog

## App para CRUD de Catálogo - usando python 3.7, aiohttp e mongo

Antes de começar, é necessário a criação e ativação de uma VirtualEnv com Python 3.7, para isso recomendo pyenv.
Também é necessário ter instalado o `docker` e o `docker-compose` para subir os `containers`.
Após isso, vá para a pasta raiz desse projeto (sfg_catalog) e siga as instruções abaixo.

1) Instale os requisitos do projeto

    ```shell
    $ make requirements
    ```

2) Suba os containers e em seguida a aplicação

    ```shell
    $ make containers
    $ make run
    ```


# Testando com curl:

NOTA: Uma alternativa ao curl é o Swagger para interagir com a API via browser. Com ele é possível fazer todas as requisições - GET, POST, PUT, PATCH e DELETE (com exceção da rota `/resources/list/`, por renderizar um HTML), acessando a seguinte URL: ``` http://127.0.0.1:8080/docs/ ```. Basta interagir com os recursos.

Os identificadores (ids) dos recursos são gerados pelo `server` com base no `sku`, `seller` e `campaign_code`, e estes não são campos editáveis.

- Retorna todos os Recursos

    ```shell
    $ curl -X GET --header 'Accept: application/json' 'http://127.0.0.1:8080/resources/'
    $ curl -X GET --header 'Accept: application/json' 'http://127.0.0.1:8080/resources/' | python -m json.tool # pretty view
    ```

    Também é possível realizar paginação (obs.: se `page` não for informado, então assume primeira página, e se `limit` não passado, o valor padrão é 20)

    ```shell
    $ curl -X GET --header 'Accept: application/json' 'http://127.0.0.1:8080/resources/?page=1&limit=5'
    ```

    Também é possível realizar filtros através das propriedades dos recursos, com exceção dos campos `id`, `list_price`, `price`. Os filtros são aplicados considerando critério de "conter", como a expressão `like` do SQL. (obs.: esses filtros não foram adicionados no swagger)

    ```shell
    $ curl -X GET --header 'Accept: application/json' 'http://127.0.0.1:8080/resources/?seller=dafiti&brand=Xuxa'
    ```

    Response:
    ```
    [
        {
            "brand": "bananas de pijama",
            "campaign_code": "buscape",
            "category": "acessorios",
            "id": "1111-tricae-buscape",
            "list_price": 99.9,
            "price": 87.89,
            "product_name": "Cinto couro com fivela de metal",
            "seller": "tricae",
            "size": "Unico",
            "sku": "1111",
            "subcategory": "cinto"
        },
    ]

    ```

- Cria um novo Recurso

    ```shell
    $ curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{
    "sku": "666XPT1",
    "seller": "dafiti",
    "campaign_code": "buscape",
    "product_name": "Chinelo amarelo",
    "brand": "Muquiranas",
    "category": "calcados",
    "subcategory": "chinelo",
    "size": "40",
    "list_price": 99.9,
    "price": 49.9
    }' 'http://127.0.0.1:8080/resources/'
    ```

    Response:
    ```
    {"sku": "666XPT1", "seller": "dafiti", "campaign_code": "buscape", "product_name": "Chinelo amarelo", "brand": "Muquiranas", "category": "calcados", "subcategory": "chinelo", "size": "40", "list_price": 99.9, "price": 49.9, "id": "666XPT1-dafiti-buscape"}
    ```

- Deleta um Recurso usando o seu identificador

    ```shell
    $ curl -X DELETE --header 'Accept: application/octet-stream' 'http://127.0.0.1:8080/resources/666XPTO-dafiti-buscape/'
    ```

    Response:
    ```
    ```

 - Retorna um Recurso especifico usando o seu identificador

    ```shell
    $ curl -X GET --header 'Accept: application/json' 'http://127.0.0.1:8080/resources/666XPTO-dafiti-buscape/'
    ```

    Response:
    ```
    {"sku": "666XPTO", "seller": "dafiti", "campaign_code": "buscape", "product_name": "Chinelo amarelo", "brand": "Muquiranas", "category": "calcados", "subcategory": "chinelo", "size": "40", "list_price": 99.9, "price": 49.9, "id": "666XPTO-dafiti-buscape"}
    ```

- Altera as propriedades de um Recurso já cadastrado usando PATCH, exceto o `id`, `sku`, `seller` e `campaign_code`. Não é necessário passar todo `payload`.

    ```shell
    $ curl -X PATCH --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{
    "brand": "pamonha",
    "list_price": 50,
    "price": 25
    }' 'http://127.0.0.1:8080/resources/666XPTO-dafiti-buscape/'
    ```

    Response:
    ```
    {"sku": "666XPTO", "seller": "dafiti", "campaign_code": "buscape", "product_name": "Chinelo amarelo", "brand": "pamonha", "category": "calcados", "subcategory": "chinelo", "size": "40", "list_price": 50, "price": 25, "id": "666XPTO-dafiti-buscape"}
    ```

- Altera os campos de um Recurso já cadastrado usando PUT, exceto o `id`, `sku`, `seller` e `campaign_code`. É necessário passar todo o `payload`.

    ```shell
    $ curl -X PUT --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{
    "sku": "666XPTO",
    "seller": "dafiti",
    "campaign_code": "buscape",
    "product_name": "Chinelo azul",
    "brand": "hue",
    "category": "pezinho",
    "subcategory": "chinelo",
    "size": "40",
    "list_price": 99.9,
    "price": 49.9
    }' 'http://127.0.0.1:8080/resources/666XPTO-dafiti-buscape/'
    ```

    Response:
    ```
    {"sku": "666XPTO", "seller": "dafiti", "campaign_code": "buscape", "product_name": "Chinelo azul", "brand": "hue", "category": "pezinho", "subcategory": "chinelo", "size": "40", "list_price": 99.9, "price": 49.9, "id": "666XPTO-dafiti-buscape"}
    ```

- Realiza upload de um arquivo csv com os Recursos a serem criados ou atualizados. (obs.: Importante definir o caminho do arquivo corretamente e respeitar a estrutura do arquivo exemplo no projeto)

    ```shell
    $ curl -F 'csv_file=@resources.csv' --header 'Content-Type: multipart/form-data' --header 'Accept: application/octet-stream' 'http://127.0.0.1:8080/resources/csv_import/'
    ```

- E por fim, a última rota lista os Recursos. Recomendo acessar no navegador por renderizar `html`:
    `http://127.0.0.1:8080/resources/list/`

# Para observar os testes, rode os seguintes comandos

Para instalar os requirements:

```shell
$ make requirements_dev
```

Para rodar os testes:

```shell
$ make test
```

Para rodar algum teste específico:

```shell
$ make test-matching Q=<Target Test>
```

Para ver a cobertura dos testes:

```shell
$ make coverage
```