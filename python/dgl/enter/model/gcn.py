#>>> import
import torch
import torch.nn as nn
from dgl.nn import GraphConv
#<<< import

class GCN(nn.Module):
    def __init__(self,
                 in_size,
                 out_size,
                 hidden_size: int = 16,
                 num_layers: int = 1,
                 norm: str = "both",
                 activation: str = "relu",
                 dropout: float = 0.5,
                 use_edge_weight: bool = False):
        """Graph Convolutional Networks

        Parameters
        ----------
        in_size : int
            Number of input features.
        out_size : int
            Output size.
        hidden_size : int
            Hidden size.
        num_layers : int
            Number of layers.
        norm : str
            GCN normalization type. Can be 'both', 'right', 'left', 'none'.
        activation : str
            Activation function.
        dropout : float
            Dropout rate.
        use_edge_weight : bool
            If true, scale the messages by edge weights.
        """
        super().__init__()
        self.use_edge_weight = use_edge_weight
        self.layers = nn.ModuleList()
        # input layer
        self.layers.append(dgl.nn.GraphConv(in_size, hidden_size, norm=norm))
        # hidden layers
        for i in range(num_layers - 1):
            self.layers.append(dgl.nn.GraphConv(hidden_size, hidden_size, norm=norm))
        # output layer
        self.layers.append(dgl.nn.GraphConv(hidden_size, out_size, norm=norm))
        self.dropout = nn.Dropout(p=dropout)
        self.act = getattr(torch, activation)

    def forward(self, g, node_feat, edge_feat):
        h = node_feat
        edge_weight = edge_feat if self.use_edge_weight else None
        for layer in self.layers[:-1]:
            h = layer(g, h, edge_weight=edge_weight)
            h = self.act(h)
            h = self.dropout(h)
        h = self.layers[-1](g, h, edge_weight=edge_weight)
        return h