# 使用方法

## 指令窗口
在Window搜索栏里输入并运行Anaconda Prompt。
运行指令
```
> D:
```
切换到D盘。运行指令
```
> cd D:\wendao_project\
```
切换到所在目录文件夹。

## Script运行方法
```
python example.py <func> <file>
```
func: 运行方式，可以是people, payment, apply中的一种
file: 数据文件

## 加人
```
python example.py people <people_file>
```

people_file的格式：
| name | parent | incash | outcash |
| --- | --- | --- | --- |
| 名字1(字符串) | 上级1(id) | 收入1(数字) | 支出1(数字) |
| 名字2(字符串) | 上级2(id) | 收入2(数字) | 支出2(数字) |
| ... | ... | ... | ... |

## 付款
```
python example.py payment <payment_file>
```

payment_file的格式：
| payer | amount | type |
| --- | --- | --- |
| 付款人1(id) | 金额1(数字) | 类型1(字符串) |
| 付款人2(id) | 金额2(数字) | 类型2(字符串) |
| ... | ... | ... |

## 确认付款
```
python example.py apply <payment_file>
```

payment_file的格式同上。

## 更改设置
utils.py里存有设置变量：
L2_THRESHOLD_NUM_PEOPLE: 获得两层分成所需人数
PERCENTAGE: 分成比例；按照以下格式来写：
```
{
	"付款类型": {"l1": 比例, "l2": 比例}, 
	"付款类型": {"l1": 比例, "l2": 比例}, 
	...
}
```
