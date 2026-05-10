from search import search_prompt

def main():
    print("Iniciando o sistema de chat RAG...")
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return
    
    print("-" * 50)
    print("Bem-vindo ao Chat do MBA IA! (Digite 'sair' para encerrar)")
    print("-" * 50)

    while True:
        query = input("\nVocê: ").strip()
        
        if query.lower() in ["sair", "exit", "quit"]:
            print("Encerrando o chat. Até logo!")
            break
        
        if not query:
            continue
            
        try:
            print("Buscando resposta...", end="\r")
            response = chain.invoke({"input": query})
            print(f"IA: {response['answer']}")
        except Exception as e:
            print(f"Erro ao processar sua pergunta: {e}")

if __name__ == "__main__":
    main()