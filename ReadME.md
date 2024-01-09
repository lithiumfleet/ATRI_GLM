# ATRI_GLM
> 项目将使用baichun2为底座.后续可能会改名.
> ~~由于ATRI本身的数据集实在太少,且没有使用gpt扩增语料的想法,项目可能会弃坑...~~
> 使用qwen造了些语料,微调后模型有初步效果.
> 停止更新.

## features

+ 更接近原作
+ 语音输入和输出

## todolist

+ [x] 整理微调经验贴
+ [x] 获取数据集
+ [x] 微调
+ [x] 记忆组件
+ [x] 外围组件

## 展示

> 采用语音输入(会有识别不准的问题), 以及ATRI语音输出.
<img width="430" alt="114718" src="https://github.com/lithiumfleet/ATRI_GLM/assets/114126477/77f05e6a-fb64-4012-950a-52e9739a47dc">

## usage

> 这个玩具项目没打算给人用......看看就好.
1. server_scripts: app.py和TTS_server.py分别放到llamafactory和moetts中以启动服务(见脚本注释).
2. 微调: ATRI语气数据集: 2.9k生成数据集(from qwen14b)和oaast_sft. 微调配置在start.sh里
3. 启动atri.py

## acknowledgements

+ chatglm.cpp[https://github.com/li-plus/chatglm.cpp]
+ LLaMA-Factory[https://github.com/hiyouga/LLaMA-Factory]
+ MoeTTS[https://github.com/luoyily/MoeTTS]
