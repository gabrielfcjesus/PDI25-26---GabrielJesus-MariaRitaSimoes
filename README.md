# PrimeTool Production

## Descrição

O PrimeTool Production é um sistema de gestão desenvolvido para apoiar o processo produtivo de uma empresa. O objetivo da aplicação é centralizar a informação e facilitar o acompanhamento das várias fases do trabalho, desde o planeamento até à expedição e montagem.


## Funcionalidades principais

- Gestão de ordens de produção
- Consulta de materiais necessários
- Controlo de stock e apoio ao armazém
- Acompanhamento da produção
- Validação pelo departamento da qualidade
- Preparação da expedição
- Consulta do estado das ordens pela equipa de montagem
- Gestão de utilizadores e permissões

## Tecnologias utilizadas

- Python
- Django
- Django REST Framework
- HTML
- CSS
- Bootstrap
- SQLite

Numa fase posterior, o sistema poderá ser adaptado para uma base de dados online, como por exemplo o Supabase.


## Estrutura do projeto

```text
primetool/
│
├── manage.py                    <- Ficheiro principal de execução do Django
├── requirements.txt            <- Dependências do projeto
├── .env.example                <- Exemplo de configuração de variáveis de ambiente
│
├── config/                     <- Configurações principais do Django
│   ├── __init__.py
│   ├── settings.py             <- Configurações gerais da aplicação
│   ├── urls.py                 <- Rotas principais do projeto
│   └── wsgi.py                 <- Configuração de deploy
│
├── apps/                       <- Aplicações do sistema
│   ├── core/                   <- Base do sistema, autenticação e permissões
│   ├── rh/                     <- Recursos Humanos
│   ├── planeamento/            <- Gestão e planeamento das ordens de produção
│   ├── armazem/                <- Gestão de materiais e stock
│   ├── producao/               <- Execução e acompanhamento da produção
│   ├── qualidade/              <- Validação e controlo de qualidade
│   ├── expedicao/              <- Preparação e gestão da expedição
│   └── montagem/               <- Acompanhamento da montagem no cliente
│
├── templates/                  <- Templates HTML do sistema
│   ├── base.html               <- Template base da aplicação
│   ├── partials/               <- Componentes reutilizáveis
│   │   ├── navbar.html
│   │   └── sidebar.html
│   ├── planeamento/            <- Templates do módulo de planeamento
│   ├── armazem/                <- Templates do módulo de armazém
│   ├── producao/               <- Templates do módulo de produção
│   ├── qualidade/              <- Templates do módulo de qualidade
│   ├── expedicao/              <- Templates do módulo de expedição
│   └── montagem/               <- Templates do módulo de montagem
│
├── static/                     <- Ficheiros estáticos
│   ├── css/                    <- Ficheiros de estilo
│   ├── js/                     <- Scripts JavaScript
│   └── img/                    <- Imagens do sistema
│
└── README.md                   <- Documento de apresentação do projeto
