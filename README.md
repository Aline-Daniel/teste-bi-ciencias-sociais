# 📊 Produção Científica - Ciências Sociais (BI Dashboard)

Este repositório contém o desenvolvimento e a arquitetura de dados (ETL + Data Warehouse) referentes ao teste técnico de Business Intelligence para análise de periódicos científicos.

Como diferencial técnico e visando a melhor experiência de usuário (UX) para a coordenação do programa, os resultados da modelagem não foram entregues apenas de forma estática: **foram integrados em uma aplicação web interativa.**

🌐 **ACESSE O DASHBOARD FUNCIONAL AQUI:** **[https://academinav-insight.lovable.app](https://academinav-insight.lovable.app)**

---

## 📂 Arquivos do Repositório

* `artigos_fi1.csv` e `artigos_fi2.csv`: Bases originais fornecidas para o teste.
* `etl_script.py`: Script Python responsável pela extração, limpeza (tratamento de dados não estruturados e conversão de tipagem) e carga na base de dados SQLite.
* `queries.sql`: Consultas SQL utilizadas para responder às perguntas de negócio.
* `producao_cientifica.db`: O banco de dados relacional final gerado pelo script, contendo as tabelas limpas e a *View* unificada para análise.

---

## 🚀 Como Executar Localmente

1. Clone o repositório para a sua máquina.
2. Certifique-se de ter o Python instalado e execute o script de ETL para processar os arquivos CSV e recriar o banco de dados:
   Bash
   
   python etl_script.py

   
🧠 Decisões Técnicas

Normalização: O script Python trata inconsistências como números com vírgulas decimais e múltiplos ISSNs por periódico.

Performance: A criação de uma VIEW unificada em SQL permite consultas rápidas cruzando dados nacionais e internacionais sem redundância.

Diferencial: Além dos dados brutos, a entrega inclui uma aplicação web moderna para facilitar a leitura dos indicadores pela coordenação.

Desenvolvido por: Aline Daniel
