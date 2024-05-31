import torch
import torch.nn as nn
import treetensor.torch as ttorch
from ding.torch_utils import Transformer, MLP, unsqueeze, to_tensor


class ItemEncoder(nn.Module):
    """
    用于对物品进行编码的模块。

    Args:
        item_obs_size (int): 物品观测空间的大小，默认为11。
        item_num (int): 物品数量，默认为180。
        item_encoder_type (str): 物品编码器的类型，可选值为'TF'、'MLP'、'two_stage_MLP'，默认为'TF'。
        hidden_size (int): 隐藏层的大小，默认为64。
        activation (torch.nn.Module): 激活函数，默认为torch.nn.ReLU()。

    Attributes:
        encoder_type (list): 物品编码器的类型列表，包含'TF'（TensorFlow）、'MLP'（多层感知器）、'two_stage_MLP'。
        item_encoder_type (str): 物品编码器的类型。
        item_num (int): 物品数量。
        hidden_size (int): 隐藏层的大小。
        encoder (torch.nn.Module): 编码器模块。

    """

    encoder_type = ['TF', 'MLP', 'two_stage_MLP']

    def __init__(self, item_obs_size=11, item_num=180, item_encoder_type='TF', hidden_size=64, activation=nn.ReLU()):
        super(ItemEncoder, self).__init__()
        assert item_encoder_type in self.encoder_type, "不支持的物品编码器类型: {}/{}".format(item_encoder_type, self.encoder_type)
        self.item_encoder_type = item_encoder_type
        self.item_num = item_num
        self.hidden_size = hidden_size

        if self.item_encoder_type == 'TF':
            self.encoder = Transformer(
                item_obs_size,
                hidden_dim=2 * hidden_size,
                output_dim=hidden_size,
                activation=activation
            )
        elif self.item_encoder_type == 'MLP':
            self.encoder = MLP(
                item_obs_size,
                hidden_size,
                hidden_size,
                layer_num=3,
                activation=activation
            )
        elif self.item_encoder_type == 'two_stage_MLP':
            self.trans_len = 16
            self.encoder_1 = MLP(
                item_obs_size,
                hidden_size,
                self.trans_len,
                layer_num=3,
                activation=activation
            )
            self.encoder_2 = MLP(
                self.trans_len*self.item_num,
                hidden_size,
                self.item_num*hidden_size,
                layer_num=2,
                activation=activation
            )

    def forward(self, item_obs):
        """
        对物品进行编码。

        Args:
            item_obs (torch.Tensor): 物品观测数据。

        Returns:
            torch.Tensor: 编码后的物品表示。

        """
        if self.item_encoder_type == 'two_stage_MLP':
            item_embedding_1 = self.encoder_1(item_obs)   # (B, M, L)
            item_embedding_2 = torch.reshape(item_embedding_1, [-1, self.trans_len*self.item_num])
            item_embedding = self.encoder_2(item_embedding_2)
            item_embedding = torch.reshape(item_embedding, [-1, self.item_num, self.hidden_size])
        else:
            if item_obs.dtype != torch.float32:
                item_obs = item_obs.float()
            item_embedding = self.encoder(item_obs)
        return item_embedding


class SheepModel(nn.Module):
    """
    SheepModel是一个神经网络模型，用于计算羊的行为和评估值。

    Args:
        item_obs_size (int): card_num列数，默认为11。
        item_num (int): 物品数量，默认为180。
        item_encoder_type (str): 物品编码器的类型，默认为'TF'。
        stack_obs_size (int): stack_positions的大小，默认为30。
        global_obs_size (int): relation的大小，默认为32400。
        hidden_size (int): 隐藏层的大小，默认为64。
        activation (nn.Module): 激活函数，默认为nn.ReLU()。
        ttorch_return (bool): 是否返回ttorch张量，默认为False。

    Attributes:
        num_encoder (ItemEncoder): card_num编码器。
        stack_encoder (MLP): stack编码器。
        relation_encoder (ItemEncoder): relation编码器。
        value_head (nn.Sequential): 价值头部网络。
        ttorch_return (bool): 是否返回ttorch张量。

    Methods:
        compute_actor: 计算行为。
        compute_critic: 计算评估值。
        compute_actor_critic: 计算行为和评估值。
        forward: 前向传播。
        compute_action: 计算动作。
    """
    mode = ['compute_actor', 'compute_critic', 'compute_actor_critic']

    def __init__(self, item_obs_size=11, item_num=180, item_encoder_type='TF', stack_obs_size=30, global_obs_size=32400, hidden_size=64, activation=nn.ReLU(), ttorch_return=False):
        super(SheepModel, self).__init__()
        self.num_encoder = ItemEncoder(item_obs_size, item_num, item_encoder_type, hidden_size, activation=activation)
        self.stack_encoder = MLP(stack_obs_size, hidden_size, hidden_size, layer_num=3, activation=activation)
        self.relation_encoder = ItemEncoder(item_num,item_num, item_encoder_type,hidden_size, activation=activation)
        self.value_head = nn.Sequential(
            MLP(hidden_size, hidden_size, hidden_size, layer_num=2, activation=activation), nn.Linear(hidden_size, 1)
        )
        self.ttorch_return = ttorch_return

    def compute_actor(self, x):
        """
        计算行为。

        Args:
            x (dict): 输入数据字典，包含以下键值对:
                - 'card_num' (Tensor): 物品数量张量。
                - 'stack_positions' (Tensor): 堆栈位置张量。
                - 'relation' (Tensor): 关系张量。
                - 'movable_cards' (Tensor): 可移动物品张量。

        Returns:
            Union[Tensor, dict]: 如果ttorch_return为True，则返回行为张量；否则返回包含行为张量的字典。
        """
        num_embedding = self.num_encoder(x['card_num'].float())
        stack_embedding = self.stack_encoder(x['stack_positions'].float())
        relation_embedding = self.relation_encoder(x['relation'].float())

        key = num_embedding+relation_embedding
        query = stack_embedding
        query = query.unsqueeze(1)
        logit = (key * query).sum(2)
        logit.masked_fill_(~x['movable_cards'].bool(), value=-1e9)
        if self.ttorch_return:
            return logit
        else:
            return {'logit': logit}

    def compute_critic(self, x):
        """
        计算评估值。

        Args:
            x (dict): 输入数据字典，包含以下键值对:
                - 'card_num' (Tensor): 物品数量张量。
                - 'stack_positions' (Tensor): 堆栈位置张量。
                - 'relation' (Tensor): 关系张量。

        Returns:
            Union[Tensor, dict]: 如果ttorch_return为True，则返回评估值张量；否则返回包含评估值张量的字典。
        """
        num_embedding = self.num_encoder(x['card_num'].float())
        stack_embedding = self.stack_encoder(x['stack_positions'].float())
        relation_embedding = self.relation_encoder(x['relation'].float())

        embedding = num_embedding.mean(1) + relation_embedding.mean(1)
        value = self.value_head(embedding)
        if self.ttorch_return:
            return value.squeeze(1)
        else:
            return {'value': value.squeeze(1)}

    def compute_actor_critic(self, x):
        """
        计算行为和评估值。

        Args:
            x (dict): 输入数据字典，包含以下键值对:
                - 'card_num' (Tensor): 物品数量张量。
                - 'stack_positions' (Tensor): 堆栈位置张量。
                - 'relation' (Tensor): 关系张量。
                - 'movable_cards' (Tensor): 可移动物品张量。

        Returns:
            Union[Tensor, dict]: 如果ttorch_return为True，则返回包含行为张量和评估值张量的ttorch张量；否则返回包含行为张量和评估值张量的字典。
        """
        num_embedding = self.num_encoder(x['card_num'].float())
        stack_embedding = self.stack_encoder(x['stack_positions'].float())
        relation_embedding = self.relation_encoder(x['relation'].float())

        key = num_embedding+ relation_embedding
        query = stack_embedding 
        query = query.unsqueeze(1)
        logit = (key * query).sum(2)
        logit.masked_fill_(~x['movable_cards'].bool(), value=-1e9)

        embedding = num_embedding.mean(1) + relation_embedding.mean(1)
        value = self.value_head(embedding)
        if self.ttorch_return:
            return ttorch.as_tensor({'logit': logit, 'value': value.squeeze(1)})
        else:
            return {'logit': logit, 'value': value.squeeze(1)}

    def forward(self, x, mode):
        """
        前向传播。

        Args:
            x (dict): 输入数据字典。
            mode (str): 前向传播模式。

        Returns:
            Union[Tensor, dict]: 根据前向传播模式返回相应的结果。
        """
        assert mode in self.mode, "not support forward mode: {}/{}".format(mode, self.mode)
        return getattr(self, mode)(x)

    def compute_action(self, x):
        """
        计算最佳动作。

        Args:
            x (dict): 输入数据字典。

        Returns:
            int: 动作的索引值。
        """
        x = unsqueeze(to_tensor(x))
        with torch.no_grad():
            logit = self.compute_actor(x)['logit']
            return logit.argmax(dim=-1)[0].item()