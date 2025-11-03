import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory


def load_config() -> tuple[str, str, float]:
    load_dotenv(override=False)
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("[ERROR] 未找到 DEEPSEEK_API_KEY。请设置环境变量后重试。", file=sys.stderr)
        sys.exit(1)

    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip() or "deepseek-chat"
    try:
        temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))
    except ValueError:
        temperature = 0.7

    return api_key, model_name, temperature


def build_conversation_chain(api_key: str, model_name: str, temperature: float) -> ConversationChain:
    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        model=model_name,
        temperature=temperature,
        timeout=60,
    )

    memory = ConversationBufferMemory(return_messages=True)
    chain = ConversationChain(llm=llm, memory=memory, verbose=False)
    return chain


def main() -> None:
    api_key, model_name, temperature = load_config()
    chain = build_conversation_chain(api_key, model_name, temperature)

    print("\nDeepSeek x LangChain 聊天机器人 (输入 exit/quit 退出)\n")
    print(f"Model: {model_name}  | Temperature: {temperature}")

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if user_input.lower() in {"exit", "quit", "q"}:
            print("再见！")
            break
        if not user_input:
            continue

        try:
            response = chain.predict(input=user_input)
            print(f"助手: {response}\n")
        except Exception as exc:
            print(f"[ERROR] 调用失败: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()


