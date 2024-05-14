from llm.llm import LLM

if __name__ == '__main__':
    llm = LLM()
    print(llm.execute_prompting("I have the homework to do on tomorrow"))