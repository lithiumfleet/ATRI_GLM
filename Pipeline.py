from requests import post

class Pipe:
  def __init__(self) -> None:
    # 我使用的cpolar的域名会变动, 在这里修改
    # 可以在这里换成自己模型api
    self.url= "localhost:7999/v1/chat/completions"
    self.default_args = {
    "do_sample": "true",
    "temperature": 0.8,
    "top_p": 0.5,
    "n": 1,
    "max_tokens": 0,
    "stream": "false"
    }
  
  def get_messages(self, query:str, history:list[str], knowledge:list[str], system:str) -> list[dict[str:str]]:
    messages = []
    # 设置system prompt
    if system == '':
      system = "你是ATRI,你需要用可爱活泼的语气回复."

    # 这里直接将knowledge拼接在system后面
    str_knowledge = '以下是一些信息:'+';'.join(knowledge)
    messages.append({"role":"system", "content":system+str_knowledge})

    # 交替设置role
    for i,text in enumerate(history):
      line = {"role":"user", "content":text} if i % 2 == 0 else {"role":"assistant", "content":text}
      messages.append(line)

    # 加入query
    messages.append({"role":"user", "content":query})
    return messages


  def chat(self,query:str='' ,history:list[str]=[], knowledge:list[str]=[], system:str='', **args) -> list[str]:
    # 合成messages
    messages = self.get_messages(query,history,knowledge,system)

    # 把其他字段加进来
    data = {"model":"ATRI","messages":messages}
    for k,v in self.default_args.items(): 
      # 如果没有传其他参数就从default_args里面找
      data[k] = v if args.get(k,None) is None else args[k]

    response = post(url=self.url, json=data)

    # 考虑到data["n"]>1时会有多个回复, 所以在这里遍历
    ans = []
    for i in range(data["n"]):
      ans.append(response.json()["choices"][i]["message"]["content"])

    return ans