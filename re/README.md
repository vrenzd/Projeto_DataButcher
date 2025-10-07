<img width="2055" height="849" alt="DataButcher excalidraw" src="https://github.com/user-attachments/assets/7829e252-c2c9-462c-a83b-25855f26413c" />


- [**main.py**](vscode-file://vscode-app/c:/Users/victo/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)
    
    - Ponto de entrada. Lê variáveis de ambiente (`MONGO_USER`, `MONGO_PASS`) via `dotenv`.
    - Cria instância de `GerenciadorMongoDB` e chama `conectar` (método `conectar` em [gerencia_BD.py](vscode-file://vscode-app/c:/Users/victo/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)).
    - Cria `GerenciaUsuario` e `GerenciadorMaquinas`, passando o gerenciador de BD.
    - Implementa menu de console para: cadastrar usuário, login, excluir usuário, adicionar máquina, listar máquinas do usuário, remover máquina, logout.
- [**gerencia_BD.py**](vscode-file://vscode-app/c:/Users/victo/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) (GerenciadorMongoDB)
    
    - Responsável pela conexão com MongoDB.
    - Métodos de nível baixo: conectar/fechar, obter coleção, inserir, buscar, atualizar, deletar.
    - Retorna objetos `pymongo` como resultados.
    - Normaliza a camada de acesso ao banco para os gerenciadores de domínio.
- [**gerencia_usuario.py**](vscode-file://vscode-app/c:/Users/victo/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) (GerenciaUsuario)
    
    - Encapsula regras de usuário:
        - `cadastrar_usuario(nome_usuario, senha)`: verifica existência; usa `bcrypt` para hash; insere em coleção `usuarios`.
            - Documento salvo: { "nome_usuario": str, "senha": str(hashed) } — a senha armazenada é string do hash (utf-8).
        - `verificar_usuario(nome_usuario, senha)`: busca usuário por `nome_usuario`, compara hash com `bcrypt.checkpw`.
        - `deletar_usuario(nome_usuario)`: remove documento por `nome_usuario`.
        - `usuario_existe(nome_usuario)`: helper booleano.
    - Usa `GerenciadorMongoDB` via composição (injeção por construtor).
- [**gerencia_maquinas.py**](vscode-file://vscode-app/c:/Users/victo/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) (GerenciadorMaquinas)
    
    - Regras para máquinas:
        - `adicionar_maquina(nome_maquina, id_usuario)`: aceita `id_usuario` como `ObjectId` ou string que será convertido; insere em coleção `maquinas`.
            - Documento salvo: { "nome_maquina": str, "id_usuario": ObjectId }
        - `listar_maquinas_por_usuario(id_usuario)`: converte `id_usuario` se necessário e realiza `find` por `id_usuario`.
        - `remover_maquina(id_maquina)`: converte `id_maquina` para `ObjectId` e remove por `_id`.
    - Também usa `GerenciadorMongoDB`.
- **Tipos / formatos importantes**
    
    - IDs: usa `bson.ObjectId` para relacionar documentos (armazenado em `maquinas.id_usuario`).
    - Coleções:
        - 'usuarios': documentos com campos `nome_usuario` (str) e `senha` (hash str).
        - 'maquinas': documentos com `nome_maquina` (str) e `id_usuario` (ObjectId referenciando `_id` em `usuarios`).
