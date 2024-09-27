# ds_20242_g1

Repositório definido para a manutenção do controle de versão dos artefatos do projeto de do Grupo 1, da Disciplina de Domínios de Software, no semestre 2024-2.

## Nome do Projeto

 ![Logo SmartCheck](docs/LogoSmartCheck.png)

### Descrição

O SmartCheck reconhecerá biometricamente os alunos do INF e integrará suas presenças diretamente ao Sigaa. Optamos por esse domínio porque ele se conecta ao meio em que estamos inseridos, o que facilita o contato com um domain expert. Além disso, a falta de um software similar ao que estamos propondo nos prejudica de certa forma, já que cada método comum de chamada apresenta vantagens e desvantagens que precisam ser ponderadas.

### Problema

Nosso problema se concentra nos tipos de chamadas mais comuns realizadas na universidade, sendo que todas possuem pontos fortes e fracos quando comparadas entre si:

1. Chamada nominal: Este tipo de chamada tem a vantagem de que os dados coletados são geralmente mais confiáveis do que os dos demais tipos, já que o professor, na maioria dos casos, realiza uma certa “verificação” dos alunos que alegam estar presentes. Em contrapartida, esse método tem a desvantagem de demandar uma parcela de tempo de todas as aulas ministradas, tempo que poderia ser utilizado para aprofundar os conceitos e atividades da disciplina.

2. Chamada por assinatura: Este tipo de chamada tem a vantagem de ser realizado sem interrupções significativas nas aulas. Porém, os dados obtidos são menos confiáveis do que os da chamada nominal, já que qualquer aluno pode facilmente burlar o sistema pedindo para outra pessoa assinar por ele e, se bem feito, isso dificilmente seria detectado pelo professor.

3. Chamada online: Tem a vantagem de poder ser realizada com interrupções praticamente nulas nas aulas. No entanto, os dados coletados por esse método são os menos confiáveis no geral, já que um aluno poderia facilmente preencher a chamada fora da sala de aula, e isso muito dificilmente seria detectado pelo professor.

### Objetivos da Solução

Como vimos acima, cada método possui vantagens e desvantagens em relação à confiabilidade dos dados colhidos e à parcela de tempo da disciplina necessária para realizá-los. O SmartCheck introduz um quarto método: a chamada biométrica, que poderia otimizar ambos os pontos levantados. Não seria necessária uma interrupção da aula para a realização da chamada, pois o próprio aluno conseguiria realizar todo o processo sozinho. Além disso, a confiabilidade dos dados seria mais alta do que em qualquer outro método, já que os alunos precisariam estar presentes para realizar a autovalidação da chamada. Por envolver biometria, também não seria possível que terceiros validassem a presença, uma vez que, novamente, seria necessário estar fisicamente presente no local para obter a presença.

Dessa forma, o SmartCheck se propõe a superar os métodos mais comuns em todos os principais quesitos, tornando-se útil em nossa realidade acadêmica, e reduzindo com eficiência um dos problemas enfrentados por alunos e professores da universidade.

### Grupo

Este projeto será desenvolvido pelos componentes do grupo 1:

|Matrícula|Nome|Usuário Git|
|---|---|---|
|202201689|FELIPE MOREIRA SILVA|[<usuario_github>](https://github.com/<usuario_github>)|
|202300194|JOSEPPE PEDRO CUNHA FELLINI|[jongas124](https://github.com/jongas124)|
|202201707|MATHEUS FRANCO CASCÃO COSTA|[matheuscascao](https://github.com/matheuscascao)|
|202204842|MAURO SÉRGIO DO NASCIMENTO JUNIOR|[omega050](https://github.com/omega050)|
|202004771|MIKHAEL MACHADO FERNANDES MAIA|[Mikanaja](https://github.com/Mikanaja)|

### Backlog do Produto

1. RF001 - O sistema deve permitir que o aluno registre sua presença usando biometria.
2. RF002 - O sistema deve confirmar a presença do aluno e enviar os dados ao Sigaa.
3. RF003 - O sistema deve exibir uma mensagem de erro caso não consiga identificar a biometria do aluno.
4. RF004 - O sistema deve verificar se o registro de presença está sendo realizado dentro do horário da aula e, se não estiver, exibir uma mensagem de erro.
5. RF005 - O sistema deve garantir que o aluno possa se autenticar apenas uma vez por entrada ou saída, concedendo apenas metade da presença se o procedimento não for completo.
6. RF006 - <Descrição do Requisito>.

### Requisitos Não Funcionais

1. RNF001 - Usabilidade: : O sistema deve, por padrão, permitir que o aluno registre sua presença até 10 minutos antes ou depois do horário de entrada/saída.
2. RNF002 - Segurança:  O sistema deve garantir que apenas alunos fisicamente presentes possam registrar sua presença.
3. RNF003 - Desempenho: O sistema deve proporcionar um processo de registro rápido, com tempo máximo de reconhecimento de 5 segundos por aluno.
4. RNF004 - Confiabilidade: O sistema deve ter uma alta taxa de acerto no reconhecimento biométrico para evitar fraudes.
5. RNF005 - Manutenibilidade:
6. RNF006 - Portabilidade: 
7. RNF007 - Conectividade: O sistema deve integrar-se com o módulo de reconhecimento biométrico e com o Sigaa para transmissão dos dados de presença.

### Regras de Negócio

1. RN01 - O registro de presença biométrica deve ser feito apenas quando o aluno está fisicamente presente e no horário correto.
2. RN02 - O aluno pode tentar registrar sua presença múltiplas vezes, mas o sistema só registrará a presença efetiva na primeira tentativa bem-sucedida
3. RN03 -  O sistema deve considerar o registro de presença inválido se realizado fora do horário de estipulado.
4. RN04 - A presença deve ser contabilizada como 50% caso o aluno não complete o registro na entrada e saída.
5. RN05 - <Descrição da Regra de Negócio>.

### Modelo Arquitetural

<Apresentar uma descrição sucinta do modelo arquitetural do Produto.>

### Modelo de Interfaces Gráficas

<Apresentar uma descrição sucinta do modelo de interfaces gráficas do Produto.>

### Tecnologia de Persistência de Dados

<Apresentar uma descrição sucinta do modelo de persistência do Produto.>

### Local do _Deploy_

O nosso planejamento inicial é hospedar nossa aplicação no Heroku ou no Firebase do Google, sendo crucial para nossa escolha a facilidade de configuração e também os recursos ofertados na versão gratuita.

### Cronograma de Desenvolvimento

|Iteração|Descrição|Data Início|Data Fim|Responsável|Situação|
|---|---|---|---|---|---|
|1|Concepção|30/08/2024|13/09/2024|Grupo|Concluída|
|2|Preparação|14/09/2024|27/09/2024|Grupo|Programada|
|3|Item(ns) do backlog <x,y,z>|28/09/2024|11/10/2024|Grupo|Programada|
|4|Item(ns) do backlog <x,y,z>|12/10/2024|25/10/2024|Grupo|Programada|
|5|Item(ns) do backlog <x,y,z>|26/10/2024|08/11/2024|Grupo|Programada|
|6|Item(ns) do backlog <x,y,z>|09/11/2024|22/11/2024|Grupo|Programada|
|7|Item(ns) do backlog <x,y,z>|23/11/2024|06/12/2024|Grupo|Programada|
|8|Apresentação do Projeto|07/12/2024|20/12/2024|Grupo|Programada|

### Iterações x Atividades

|Iteração|Tarefa|Data Início|Data Fim|Responsável|Situação|
|---|---|---|---|---|---|
|1|Definição do grupo de trabalho|30/08/2024|30/08/2024|Grupo|Concluída|
|1|Definição do Tema do Trabalho|30/08/2024|13/09/2024|Grupo|Concluída|
|2|Definição do Backlog do produto|13/09/2024|27/09/2024|Grupo|Programada|
|2|Descrição dos itens do backlog do produto|14/09/2024|27/09/2024|Grupo|Programada|
|2|Distribuição dos itens do backlog entre as iterações|14/09/2024|27/09/2024|Grupo|Programada|
|2|Definição do modelo arquitetural|14/09/2024|27/09/2024|Grupo|Programada|
|3|Especificação de estórias de usuários dos Item(ns) do backlog <x,y,z>|28/09/2024|11/10/2024||Programada|
|3|Diagrama de classes dos Item(ns) do backlog <x,y,z>|28/09/2024|11/10/2024||Programada|
|3|Diagrama de interação/sequencia dos itens do backlog <x,y,z>|28/09/2024|11/10/2024||Programada|
|3|Projeto de Interfaces gráficas dos itens do backlog <x,y,z>|28/09/2024|11/10/2024||Programada|
|3|Projeto de persistência dos itens do backlog <x,y,z>|28/09/2024|11/10/2024||Programada|
|3|Implementação dos itens do backlog <x,y,z>*|28/09/2024|11/10/2024||Programada|
|4|Especificação de estórias de usuários dos Item(ns) do backlog <x,y,z>|12/10/2024|25/10/2024||Programada|
|4|Diagrama de classes dos Item(ns) do backlog <x,y,z>|12/10/2024|25/10/2024||Programada|
|4|Diagrama de interação/sequencia dos itens do backlog <x,y,z>|12/10/2024|25/10/2024||Programada|
|4|Projeto de Interfaces gráficas dos itens do backlog <x,y,z>|12/10/2024|25/10/2024||Programada|
|4|Projeto de persistência dos itens do backlog <x,y,z>|12/10/2024|25/10/2024||Programada|
|4|Implementação dos itens do backlog <x,y,z>*|12/10/2024|25/10/2024||Programada|
|5|Especificação de estórias de usuários dos Item(ns) do backlog <x,y,z>|26/10/2024|08/11/2024||Programada|
|5|Diagrama de classes dos Item(ns) do backlog <x,y,z>|26/10/2024|08/11/2024||Programada|
|5|Diagrama de interação/sequencia dos itens do backlog <x,y,z>|26/10/2024|08/11/2024||Programada|
|5|Projeto de Interfaces gráficas dos itens do backlog <x,y,z>|26/10/2024|08/11/2024||Programada|
|5|Projeto de persistência dos itens do backlog <x,y,z>|26/10/2024|08/11/2024||Programada|
|5|Implementação dos itens do backlog <x,y,z>*|26/10/2024|08/11/2024||Programada|
|6|Especificação de estórias de usuários dos Item(ns) do backlog <x,y,z>|09/11/2024|22/11/2024||Programada|
|6|Diagrama de classes dos Item(ns) do backlog <x,y,z>|09/11/2024|22/11/2024||Programada|
|6|Diagrama de interação/sequencia dos itens do backlog <x,y,z>|09/11/2024|22/11/2024||Programada|
|6|Projeto de Interfaces gráficas dos itens do backlog <x,y,z>|09/11/2024|22/11/2024||Programada|
|6|Projeto de persistência dos itens do backlog <x,y,z>|09/11/2024|22/11/2024||Programada|
|6|Implementação dos itens do backlog <x,y,z>*|09/11/2024|22/11/2024||Programada|
|7|Especificação de estórias de usuários dos Item(ns) do backlog <x,y,z>|23/11/2024|06/12/2024||Programada|
|7|Diagrama de classes dos Item(ns) do backlog <x,y,z>|23/11/2024|06/12/2024||Programada|
|7|Diagrama de interação/sequencia dos itens do backlog <x,y,z>|23/11/2024|06/12/2024||Programada|
|7|Projeto de Interfaces gráficas dos itens do backlog <x,y,z>|23/11/2024|06/12/2024||Programada|
|7|Projeto de persistência dos itens do backlog <x,y,z>|23/11/2024|06/12/2024||Programada|
|7|Implementação dos itens do backlog <x,y,z>*|23/11/2024|06/12/2024||Programada|
|8|Apresentação do Projeto|07/12/2024|20/12/2024|Grupo|Programada|

* Implementação se aplicará, se os itens da iteração em andamento, forem eleitos para validação do projeto do trabalho.
