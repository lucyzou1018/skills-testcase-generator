# Demo Requirements

## 登录接口
Type: api
Summary: 用户使用用户名和密码登录系统
Prerequisites:
- 用户账号已激活
Acceptance:
- 成功登录
- 密码错误 5 次触发锁定
Constraints:
- 用户名必填，<=64 字符
- 密码必填，区分大小写
Data:
- username: string / required / max 64
- password: string / required

## 商品列表组件
Type: frontend
Acceptance:
- 加载商品卡片
- 无数据展示空态
- 选择筛选条件重新渲染
Constraints:
- 空态需展示“暂无数据”

## 质押合约
Type: contract
Prerequisites:
- 用户钱包有足够余额
Acceptance:
- 成功质押
- 质押金额不足被拒绝
- 早退触发罚息
Constraints:
- 最小质押 1 Token

## 单元测试模板
Type: unit
Acceptance:
- 测试 add() 正常结果
- 测试 sub() 负数输入
- 测试 sub() 边界值
