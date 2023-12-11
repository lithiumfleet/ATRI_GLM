# ATRI_GLM
> 项目将使用baichun2为底座.后续可能会改名.
> 由于ATRI本身的数据集实在太少,且没有使用gpt扩增语料的想法,项目可能会弃坑...

## features

+ 轻量化,少依赖
+ 更接近原作

## usage
1. 安装环境.
2. 在项目目录下创建knowledge.txt, 在里面放入任何角色预设.
3. 使用模型的api脚本得到url.
4. 在Pipeline.py中加入url, 具体看注释.
5. 启动即可.

## todolist

+ [x] 整理微调经验贴
+ [x] 获取数据集
+ [x] 微调
+ [ ] 记忆组件(待优化)
+ [ ] 推理加速

## acknowledgements

+ chatglm.cpp[https://github.com/li-plus/chatglm.cpp]
+ LLaMA-Factory[https://github.com/hiyouga/LLaMA-Factory]
