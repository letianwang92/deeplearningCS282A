import numpy as np

from deeplearning.layers import *
from deeplearning.fast_layers import *
from deeplearning.layer_utils import *


class ThreeLayerConvNet(object):
  """
  A three-layer convolutional network with the following architecture:
  
  conv - relu - 2x2 max pool - affine - relu - affine - softmax
  
  The network operates on minibatches of data that have shape (N, C, H, W)
  consisting of N images, each with height H and width W and with C input
  channels.
  """
  
  def __init__(self, input_dim=(3, 32, 32), num_filters=32, filter_size=7,
               hidden_dim=100, num_classes=10, weight_scale=1e-3, reg=0.0,
               dtype=np.float32, use_batchnorm=False):
    """
    Initialize a new network.
    
    Inputs:
    - input_dim: Tuple (C, H, W) giving size of input data
    - num_filters: Number of filters to use in the convolutional layer
    - filter_size: Size of filters to use in the convolutional layer
    - hidden_dim: Number of units to use in the fully-connected hidden layer
    - num_classes: Number of scores to produce from the final affine layer.
    - weight_scale: Scalar giving standard deviation for random initialization
      of weights.
    - reg: Scalar giving L2 regularization strength
    - dtype: numpy datatype to use for computation.
    """
    self.params = {}
    self.reg = reg
    self.dtype = dtype
    
    ############################################################################
    # TODO: Initialize weights and biases for the three-layer convolutional    #
    # network. Weights should be initialized from a Gaussian with standard     #
    # deviation equal to weight_scale; biases should be initialized to zero.   #
    # All weights and biases should be stored in the dictionary self.params.   #
    # Store weights and biases for the convolutional layer using the keys 'W1' #
    # and 'b1'; use keys 'W2' and 'b2' for the weights and biases of the       #
    # hidden affine layer, and keys 'W3' and 'b3' for the weights and biases   #
    # of the output affine layer.                                              #
    ############################################################################
    self.use_batchnorm = use_batchnorm
    self.bn_params = []
    if self.use_batchnorm:
      self.bn_params = [{'mode': 'train'} for i in xrange(2)]
    #print self.bn_params
    output_dim=num_classes
    C,H,W=input_dim
    HH=filter_size
    WW=filter_size
    pool_height=2
    pool_width=2
    stride=1
    pad=(filter_size - 1) / 2
    H_prime = 1 + (H + 2 * pad - HH) / stride/pool_height
    W_prime= 1 + (W + 2 * pad - WW) / stride/pool_width
    conv_dim=num_filters*H_prime*W_prime
    bn_dim=conv_dim
    
    self.params['W1'] = weight_scale * np.random.randn(num_filters,C,filter_size,filter_size)
    self.params['b1'] = np.zeros(num_filters)
    if self.use_batchnorm:
            self.params['gamma1'] = np.ones(num_filters)
            self.params['beta1' ] = np.zeros(num_filters)
            self.params['gamma2'] = np.ones(hidden_dim)
            self.params['beta2' ] = np.zeros(hidden_dim)

    #print self.params['W1'].shape
    self.params['W2'] = weight_scale * np.random.randn(conv_dim, hidden_dim)
    self.params['b2'] = np.zeros(hidden_dim)
    
    self.params['W3'] = weight_scale * np.random.randn(hidden_dim, output_dim)
    self.params['b3'] = np.zeros(output_dim)

    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    for k, v in self.params.iteritems():
      self.params[k] = v.astype(dtype)
     
 
  def loss(self, X, y=None):
    """
    Evaluate loss and gradient for the three-layer convolutional network.
    
    Input / output: Same API as TwoLayerNet in fc_net.py.
    """
    W1, b1 = self.params['W1'], self.params['b1']
    W2, b2 = self.params['W2'], self.params['b2']
    W3, b3 = self.params['W3'], self.params['b3']
    
    # pass conv_param to the forward pass for the convolutional layer
    filter_size = W1.shape[2]
    conv_param = {'stride': 1, 'pad': (filter_size - 1) / 2}

    # pass pool_param to the forward pass for the max-pooling layer
    pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

    scores = None
    ############################################################################
    # TODO: Implement the forward pass for the three-layer convolutional net,  #
    # computing the class scores for X and storing them in the scores          #
    # variable.                                                                #
    ############################################################################
    if self.use_batchnorm:

        conv_out, cache1 = conv_bn_relu_pool_forward(X, W1, b1, conv_param, pool_param,
                                                                    self.params['gamma1'],
                                                                    self.params['beta1'],
                                                                    self.bn_params[0])
        out2, cache2=affine_bn_relu_forward(conv_out,W2,b2,         self.params['gamma2'],
                                                                    self.params['beta2'],
                                                                    self.bn_params[1])
    else:
        conv_out,cache1=conv_relu_pool_forward(X,W1,b1,conv_param,pool_param)
        out2, cache2=affine_relu_forward(conv_out,W2,b2)
    #input_affine=conv_out.reshape((N,F*H_prime*W_prime))
    
    
    scores, cache3=affine_forward(out2,W3,b3)

    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    if y is None:
      return scores
    
    loss, grads = 0, {}
    ############################################################################
    # TODO: Implement the backward pass for the three-layer convolutional net, #
    # storing the loss and gradients in the loss and grads variables. Compute  #
    # data loss using softmax, and make sure that grads[k] holds the gradients #
    # for self.params[k]. Don't forget to add L2 regularization!               #
    ############################################################################
    loss, dscores = softmax_loss(scores, y)
    loss += 0.5 * self.reg*(np.sum(self.params['W1']* self.params['W1']) 
         + np.sum(self.params['W2']* self.params['W2'])+np.sum(self.params['W3']* self.params['W3']))
    
    dout2, dW3, grads['b3']=affine_backward(dscores, cache3)
    grads['W3']=dW3+self.reg*self.params['W3']
    

    if self.use_batchnorm:
        dout1, dW2, grads['b2'],grads['gamma2'],grads['beta2']=affine_bn_relu_backward(dout2,cache2)
        grads['W2']=dW2+self.reg*self.params['W2']
        dx, dW1, grads['b1'],grads['gamma1'],grads['beta1'] = conv_bn_relu_pool_backward(dout1, cache1)


    else: 
        dout1, dW2, grads['b2']=affine_relu_backward(dout2,cache2)
        grads['W2']=dW2+self.reg*self.params['W2']
        dx, dW1, grads['b1']=conv_relu_pool_backward(dout1, cache1)
    
    grads['W1']=dW1+self.reg*self.params['W1']
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    return loss, grads
  
  
pass
