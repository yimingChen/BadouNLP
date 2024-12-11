import torch
import torch.nn as nn
import numpy as np
import random
import json
import matplotlib.pyplot as plt

"""

基于pytorch框架编写模型训练
实现一个自行构造的找规律(机器学习)任务
规律：x是一个5维向量，如果第1个数>第5个数，则为正样本，反之为负样本

"""


class TorchModel(nn.Module):
    def __init__(self, input_size,num_classes):
        super(TorchModel, self).__init__()
        self.linear = nn.Linear(input_size, num_classes)  # 设置编号
        #self.activation = torch.sigmoid  # nn.sigmoid() sigmoid归一化函数
        self.loss = nn.CrossEntropyLoss()  #课上说过用交叉熵

    # 当输入真实标签，返回loss值；无真实标签，返回预测值
    def forward(self, x):
        return self.linear(x)  # 输出未经过激活函数的 logits


# 生成一个样本, 样本的生成方法，代表了我们要学习的规律
# 随机生成一个5维向量，如果第一个值大于第五个值，认为是正样本，反之为负样本
def build_sample():
    x = np.random.random(5)
    max_index = np.argmax(x)  # 找到最大值所在的维度作为标签
    return torch.FloatTensor(x), max_index


# 随机生成一批样本

def build_dataset(total_sample_num):# 生成训练集
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append(y)
    return torch.stack(X), torch.tensor(Y)  # 返回的是张量

# 测试代码
# 用来测试每轮模型的准确率
def evaluate(model):
    model.eval()#告诉他不是训练现在
    test_sample_num = 100
    x, y = build_dataset(test_sample_num)
    #print("本次预测集中共有%d个正样本，%d个负样本" % (sum(y), test_sample_num - sum(y)))
    correct, wrong = 0, 0
    with torch.no_grad():
        logits = model(x)
        _, preds = torch.max(logits, dim=1)  # 获取每个样本的最大类别索引
        correct = (preds == y).sum().item()  # 计算正确预测的数量
        wrong = test_sample_num - correct
    accuracy = correct / (correct + wrong)
    print(f"正确预测个数：{correct}, 正确率：{accuracy:.4f}")
    return accuracy
    # with torch.no_grad():#告诉不用计算梯度
    #     y_pred = model(x)  # 模型预测 model.forward(x)
    #     for y_p, y_t in zip(y_pred, y):  # 与真实标签进行对比
    #         if float(y_p) < 0.5 and int(y_t) == 0:
    #             correct += 1  # 负样本判断正确
    #         elif float(y_p) >= 0.5 and int(y_t) == 1:
    #             correct += 1  # 正样本判断正确
    #         else:
    #             wrong += 1
    # print("正确预测个数：%d, 正确率：%f" % (correct, correct / (correct + wrong)))
    # return correct / (correct + wrong)


def main():
    # 配置参数
    epoch_num = 20  # 训练轮数
    batch_size = 20  # 每次训练样本个数
    train_sample = 5000  # 每轮训练总共训练的样本总数
    input_size = 5  # 输入向量维度
    num_classes = 5  # 类别数（对应5维向量的索引）
    learning_rate = 0.001  # 学习率
    # 建立模型
    model = TorchModel(input_size,num_classes)
    # 选择优化器 相当于求导
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    # 创建训练集，正常任务是读取训练集
    train_x, train_y = build_dataset(train_sample)
    # 训练过程
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        for batch_index in range(train_sample // batch_size):
            x = train_x[batch_index * batch_size : (batch_index + 1) * batch_size]#依次取出 20个样本
            y = train_y[batch_index * batch_size : (batch_index + 1) * batch_size]
            optim.zero_grad()  # 梯度清零
            logits = model(x)
            loss = model.loss(logits, y)  # 计算交叉熵损失
            loss.backward()  # 反向传播
            optim.step()  # 更新权重
            watch_loss.append(loss.item())
        print(f"第{epoch + 1}轮平均loss: {np.mean(watch_loss):.4f}")
        acc = evaluate(model)  # 测试本轮模型结果
        log.append([acc, np.mean(watch_loss)])
    # 保存模型
    torch.save(model.state_dict(), "model.bin")
    # 画图
    print(log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    return


# 使用训练好的模型做预测
def predict(model_path, input_vec):
    input_size = 5
    num_classes = 5
    model = TorchModel(input_size,num_classes)
    model.load_state_dict(torch.load(model_path))  # 加载训练好的权重
    #print(model.state_dict())

    model.eval()  # 测试模式
    with torch.no_grad():  # 不计算梯度
        result = model(torch.FloatTensor(input_vec))  # 模型预测
        _, preds = torch.max(result, dim=1)  # 获取预测的类别
    for vec, pred in zip(input_vec, preds):
        print(f"输入：{vec}, 预测类别：{pred.item()}")  # 打印结果


if __name__ == "__main__":
    main()
    test_vec = [[0.07889086,0.15229675,0.31082123,0.03504317,0.88920843],
                [0.74963533,0.5524256,0.95758807,0.95520434,0.84890681],
                [0.00797868,0.67482528,0.13625847,0.34675372,0.19871392],
                [0.09349776,0.59416669,0.92579291,0.41567412,0.1358894]]
    predict("model.bin", test_vec)
