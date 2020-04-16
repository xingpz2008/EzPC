'''

Authors: Shubham Ugare.

Copyright:
Copyright (c) 2018 Microsoft Research
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import AST.AST as AST
from onnx import mapping
from onnx import TensorProto
from numbers import Number

DEBUG = False
out_var_prefix = 'J'

class OnnxNode(object):
  """
  Reimplementation of NodeProto from ONNX, but in a form
  more convenient to work with from Python.
  """

  def __init__(self, node):
    self.name = str(node.name)
    self.op_type = str(node.op_type)
    self.domain = str(node.domain)
    self.attrs = dict([(attr.name,
                       translate_onnx(attr.name, convert_onnx(attr)))
                       for attr in node.attribute])
    self.inputs = list(node.input)
    self.outputs = list(node.output)
    self.node_proto = node

__onnx_attr_translator = {
    "axis": lambda x: int(x),
    "axes": lambda x: [int(a) for a in x],
    "dtype": lambda x: onnx2seedot(x),
    "keepdims": lambda x: bool(x),
    "to": lambda x: onnx2seedot(x),
}


def convert_onnx(attr):
  return __convert_onnx_attribute_proto(attr)


def __convert_onnx_attribute_proto(attr_proto):
  """
  Convert an ONNX AttributeProto into an appropriate Python object
  for the type.
  NB: Tensor attribute gets returned as the straight proto.
  """
  if attr_proto.HasField('f'):
    return attr_proto.f
  elif attr_proto.HasField('i'):
    return attr_proto.i
  elif attr_proto.HasField('s'):
    return str(attr_proto.s, 'utf-8') if IS_PYTHON3 else attr_proto.s
  elif attr_proto.HasField('t'):
    return attr_proto.t  # this is a proto!
  elif attr_proto.HasField('g'):
    return attr_proto.g
  elif attr_proto.floats:
    return list(attr_proto.floats)
  elif attr_proto.ints:
    return list(attr_proto.ints)
  elif attr_proto.strings:
    str_list = list(attr_proto.strings)
    if IS_PYTHON3:
      str_list = list(map(lambda x: str(x, 'utf-8'), str_list))
    return str_list
  elif attr_proto.HasField('sparse_tensor'):
    return attr_proto.sparse_tensor
  else:
    raise ValueError("Unsupported ONNX attribute: {}".format(attr_proto))

def translate_onnx(key, val):
  return __onnx_attr_translator.get(key, lambda x: x)(val)

def onnx2seedot(dtype):
  return TENSOR_TYPE_TO_SEEDOT_TYPE[_onnx_dtype(dtype)] 	

def _onnx_dtype(dtype):
  if isinstance(dtype, Number):
    onnx_dype = dtype
  elif isinstance(dtype, str):
    onnx_dype = TensorProto.DataType.Value(dtype)
  else:
    raise RuntimeError("dtype should be number or str.")
  return onnx_dype  

TENSOR_TYPE_TO_SEEDOT_TYPE = {
    int(TensorProto.FLOAT): 'float32',
    int(TensorProto.UINT8): 'uint8',
    int(TensorProto.INT8): 'int8',
    int(TensorProto.UINT16): 'uint16',
    int(TensorProto.INT16): 'int16',
    int(TensorProto.INT32): 'int32',
    int(TensorProto.INT64): 'int64',
    int(TensorProto.BOOL): 'bool',
    int(TensorProto.FLOAT16): 'float16',
    int(TensorProto.DOUBLE): 'float64',
    int(TensorProto.COMPLEX64): 'complex64',
    int(TensorProto.COMPLEX128): 'complex128',
    int(TensorProto.UINT32): 'uint32',
    int(TensorProto.UINT64): 'uint64',
    int(TensorProto.STRING): 'string'
}

def getOperatorsIdx(token):
		#TODO : remove usage of this
		return AST.Operators.convSymbolToEnumValue(token)

def get_seedot_shape_order(old_shape):
	if(len(old_shape) == 4):
		# Case when spatial dimension is 2
		# inverse of [1, 3, 4, 2] is [1, 4, 2, 3]
		return ([old_shape[0], old_shape[2], old_shape[3], old_shape[1]], [1, 4, 2, 3])	
	else:
		# Casr when spatial dimension is 3 	
		# inverse of [1, 3, 4, 5, 2] is [1, 5, 2, 3, 4]
		return ([old_shape[0], old_shape[2], old_shape[3], old_shape[4], old_shape[1]], [1, 5, 2, 3, 4])

def get_seedot_filter_shape_order(filter_shape):
	if(len(filter_shape) == 4):
		# Case when spatial dimension is 2
		# inverse of [3, 4, 2, 1] is [4, 3, 1, 2]
		return ([filter_shape[2], filter_shape[3], filter_shape[1], filter_shape[0]], [4, 3, 1, 2])	
	else:
		# Casr when spatial dimension is 3 	
		# inverse of [3, 4, 5, 2, 1] is [5, 4, 1, 2, 3]
		return ([filter_shape[2], filter_shape[3], filter_shape[4], filter_shape[1], filter_shape[0]], [5, 4, 1, 2, 3])		

def get_onnx_order(onnx_shape):
	if(len(onnx_shape) == 4):
		# inverse of [1, 4, 2, 3] is [1, 3, 4, 2]
		return [1, 3, 4, 2]
	else:
		# inverse of [1, 5, 2, 3, 4] is [1, 3, 4, 5, 2]
		return [1, 3, 4, 5, 2]			

def get_reshaped_input_ast(input_name, value_info, node_name_to_out_var_dict):
	onnx_input_shape = list(value_info[input_name][1])
	(seedot_input_shape, seedot_input_order) = get_seedot_shape_order(onnx_input_shape)
	return AST.Reshape(AST.ID(node_name_to_out_var_dict[input_name]), seedot_input_shape, seedot_input_order)

def get_reshaped_bias_ast(bias_name, value_info, node_name_to_out_var_dict, dim):
	if(dim == 2):
		return AST.Reshape(AST.ID(node_name_to_out_var_dict[bias_name]), [1, 1, 1, value_info[bias_name][1][0]], None)		
	else:	
		return AST.Reshape(AST.ID(node_name_to_out_var_dict[bias_name]), [1, 1, 1, 1, value_info[bias_name][1][0]], None)		

def get_reshaped_filter_ast(filter_name, value_info, node_name_to_out_var_dict):
	onnx_filter_shape = list(value_info[filter_name][1])
	(seedot_filter_shape, seedot_filter_order) = get_seedot_filter_shape_order(onnx_filter_shape)
	return AST.Reshape(AST.ID(node_name_to_out_var_dict[filter_name]), seedot_filter_shape, seedot_filter_order)		

def get_reshaped_output_ast(onnx_output_name, value_info, output_name):	
	onnx_output_shape = list(value_info[onnx_output_name][1])
	onnx_output_order = get_onnx_order(onnx_output_shape)
	return AST.Reshape(AST.ID(output_name), onnx_output_shape, onnx_output_order)

def get_new_var_name(out_var_count):
	return out_var_prefix + str(out_var_count)
	
def update_program_with_new_node(innermost_let_ast_node, new_node, new_node_name, mtdAST):
	cur_out_var_ast_node = AST.ID(new_node_name)
	new_let_node = AST.Let(cur_out_var_ast_node, new_node, cur_out_var_ast_node)
	mtdAST.visit(new_let_node, {AST.ASTNode.mtdKeyTFOpName : 'no', AST.ASTNode.mtdKeyTFNodeName : 'no'})
	# Updating the innermost Let AST node and the expression for previous Let Node 
	innermost_let_ast_node.expr = new_let_node
	innermost_let_ast_node = new_let_node

	# node_name_to_out_var_dict[node.outputs[0]] = new_node_name
	return innermost_let_ast_node

class ONNXNodesAST:

	# value_info: dictionary of name -> (type, dimension tuple)
	def Input(node, value_info, node_name_to_out_var_dict):
		if(DEBUG):
			print(node.outputs[0])
		# There are two types of inputs
		dims = list(node.dims if hasattr(node, 'dims') else ([val.dim_value for val in  node.type.tensor_type.shape.dim]))	
		data_type = node.data_type if hasattr (node, 'data_type') else node.type.tensor_type.elem_type
		return AST.Input(dims, onnx2seedot(data_type))


	def Cast(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 
		if(DEBUG):
			print(node)
		inputsRef = node.inputs
		assert(len(inputsRef) == 1)
		# destType = node.attrs['to']

		# seedot_output_ast = AST.UninterpFuncCall(value_info[node.outputs[0]][1],
		# 									'Cast', 
		# 									[AST.ID(inputsRef[0]), 
		# 									AST.ID(destType),
		# 									AST.ID(destType)
		# 									])
		# output_name = get_new_var_name(out_var_count)
		# innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		# out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = inputsRef[0]

		return (innermost_let_ast_node, out_var_count)

	def Relu(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 

		inputsRef = node.inputs
		assert(len(inputsRef)==1)
		

		reshaped_input_name = get_new_var_name(out_var_count)
		reshaped_input = get_reshaped_input_ast(inputsRef[0], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input, reshaped_input_name, mtdAST)
		out_var_count += 1

		seedot_output_ast = AST.Func(getOperatorsIdx('relu'), AST.ID(reshaped_input_name))
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		reshaped_output_name = get_new_var_name(out_var_count)
		onnx_output_ast = get_reshaped_output_ast(node.outputs[0], value_info, output_name)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, onnx_output_ast, reshaped_output_name, mtdAST)	
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = reshaped_output_name

		if(DEBUG):
			print(node.outputs[0])
			print(onnx_input_shape, '->', seedot_input_shape, '->', onnx_output_shape)

		return (innermost_let_ast_node, out_var_count)	
		# return AST.Func(getOperatorsIdx('relu'), AST.ID(node_name_to_out_var_dict[inputsRef[0]]))

	def Add(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 
		if(DEBUG):
			print(node)
		inputsRef = node.inputs
		assert(len(inputsRef) == 2)

		reshaped_input_name = get_new_var_name(out_var_count)
		reshaped_input = get_reshaped_input_ast(inputsRef[0], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input, reshaped_input_name, mtdAST)
		out_var_count += 1

		reshaped_input_name1 = get_new_var_name(out_var_count)
		reshaped_input1 = get_reshaped_input_ast(inputsRef[1], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input1, reshaped_input_name1, mtdAST)
		out_var_count += 1

		seedot_output_ast = AST.BOp(AST.ID(reshaped_input_name),
							getOperatorsIdx('+'),
							AST.ID(reshaped_input_name1)
							)
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		
		reshaped_output_name = get_new_var_name(out_var_count)
		onnx_output_ast = get_reshaped_output_ast(node.outputs[0], value_info, output_name)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, onnx_output_ast, reshaped_output_name, mtdAST)
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = reshaped_output_name

		if(DEBUG):
			print(node.outputs[0])
			print(onnx_input_shape, onnx_input_shape1, '->', seedot_input_shape, seedot_input_shape1, '->', onnx_output_shape)

		return (innermost_let_ast_node, out_var_count)


	def Gemm(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node)
		if(DEBUG):
			print(node)
		inputsRef = node.inputs
		assert(len(inputsRef) == 3)
		input1AST = AST.ID(node_name_to_out_var_dict[inputsRef[0]])
		input2AST = AST.ID(node_name_to_out_var_dict[inputsRef[1]])

		if(node.attrs['transA']): input1AST = AST.Transp(input1AST)
		if(node.attrs['transB']): input2AST = AST.Transp(input2AST)

		# W*x + b
		seedot_output_ast = AST.BOp(AST.BOp(input1AST, getOperatorsIdx('*'), input2AST), getOperatorsIdx('+'), AST.ID(node_name_to_out_var_dict[inputsRef[2]]))
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		node_name_to_out_var_dict[node.outputs[0]] = output_name

		return (innermost_let_ast_node, out_var_count)


	def Concat(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node)
		if(DEBUG):
			print(node)
		inputsRef = node.inputs
		assert(len(inputsRef) == 2)
		input1AST = AST.ID(node_name_to_out_var_dict[inputsRef[0]])
		input2AST = AST.ID(node_name_to_out_var_dict[inputsRef[1]])

		axis = node.attrs['axis']

		seedot_output_ast = AST.UninterpFuncCall(list(value_info[node.outputs[0]][1]),
									 'Concat2T', 
									 [input1AST, input2AST, AST.Int(axis)],
									outputDiffInpDims=1
									) 

		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		node_name_to_out_var_dict[node.outputs[0]] = output_name

		return (innermost_let_ast_node, out_var_count)	

	def Constant(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node)
		if(DEBUG):
			print(node)	
		# TODO: Use AST.decl for defining a tensor. If used as a parameter for Reshape then we don't need it for now.
		return (innermost_let_ast_node, out_var_count)	

	def Transpose(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 
		if(DEBUG):
			print(node)

		inputsRef = node.inputs
		assert(len(inputsRef)==1)

		seedot_output_ast = AST.Transpose(AST.ID(node_name_to_out_var_dict[inputsRef[0]]), node.attrs['perm'])
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = output_name

		return (innermost_let_ast_node, out_var_count)	

	def Split(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node)
		# TODO: Used in shufflenetv2. Currently, onnx shape inference does not support `split`  
		return (innermost_let_ast_node, out_var_count)		

	def BatchNormalization(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 
		
		inputsRef = node.inputs
		# Are running mean and var used for something?
		assert(len(inputsRef)==5)

		reshaped_input_name = get_new_var_name(out_var_count)
		reshaped_input = get_reshaped_input_ast(inputsRef[0], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input, reshaped_input_name, mtdAST)
		out_var_count += 1

		seedot_output_ast = AST.FusedBatchNorm(AST.ID(reshaped_input_name),
										 AST.ID(node_name_to_out_var_dict[inputsRef[1]]),
										 AST.ID(node_name_to_out_var_dict[inputsRef[2]]),
										)	
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		reshaped_output_name = get_new_var_name(out_var_count)
		onnx_output_ast = get_reshaped_output_ast(node.outputs[0], value_info, output_name)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, onnx_output_ast, reshaped_output_name, mtdAST)	
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = reshaped_output_name
		
		if(DEBUG):
			print(node.outputs[0])
			print(onnx_input_shape, '->', seedot_input_shape, '->', onnx_output_shape)

		return (innermost_let_ast_node, out_var_count) 	

	def Reshape(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 
		if(DEBUG):
			print(node)

		inputsRef = node.inputs
		assert(len(inputsRef)==2)
		# print(list(value_info[node.outputs[0]][1]))

		seedot_output_ast = AST.Reshape(AST.ID(node_name_to_out_var_dict[inputsRef[0]]), list(value_info[node.outputs[0]][1]), None)
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = output_name

		return (innermost_let_ast_node, out_var_count)
	
	def Flatten(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 
		if(DEBUG):
			print(node)

		inputsRef = node.inputs
		assert(len(inputsRef)==1)

		seedot_output_ast = AST.Reshape(AST.ID(node_name_to_out_var_dict[inputsRef[0]]), list(value_info[node.outputs[0]][1]), None)
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = output_name

		return (innermost_let_ast_node, out_var_count)		

	def Conv(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 
		if(DEBUG):
			print(node)

		inputsRef = node.inputs
		# since two dimensions represent N: Number of batches and CI: Input channel
		inputShape = value_info[inputsRef[0]][1]
		spatial_size = len(inputShape)-2
		if spatial_size == 2:
			(innermost_let_ast_node, out_var_count, output_name) = ONNXNodesAST.conv2d(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST)
		elif spatial_size == 3:
			(innermost_let_ast_node, out_var_count, output_name) = ONNXNodesAST.conv3d(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST)

		reshaped_output_name = get_new_var_name(out_var_count)
		onnx_output_ast = get_reshaped_output_ast(node.outputs[0],value_info, output_name)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, onnx_output_ast, reshaped_output_name, mtdAST)
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = reshaped_output_name

		return (innermost_let_ast_node, out_var_count)

	def conv2d(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		inputsRef = node.inputs
		inputShape = value_info[inputsRef[0]][1]
		filterShape = value_info[inputsRef[1]][1]

		stridesUsed = node.attrs['strides']

		assert(len(inputsRef)==2 or len(inputsRef)==3)
		assert(len(stridesUsed)==2)
		assert(value_info[node.inputs[1]][1][2:] == tuple(node.attrs['kernel_shape']))
		# verify this order
		[zPadHLeft, zPadHRight, zPadWLeft, zPadWRight] = node.attrs['pads']

		options = {}
		options[AST.PaddingKeysDict.FH] = filterShape[2]
		options[AST.PaddingKeysDict.FW] = filterShape[3]
		options[AST.PaddingKeysDict.zPadHLeft] = zPadHLeft
		options[AST.PaddingKeysDict.zPadHRight] = zPadHRight
		options[AST.PaddingKeysDict.zPadWLeft] = zPadWLeft
		options[AST.PaddingKeysDict.zPadWRight] = zPadWRight
		options[AST.PaddingKeysDict.strideH] = stridesUsed[0]
		options[AST.PaddingKeysDict.strideW] = stridesUsed[1]
		options[AST.PaddingKeysDict.ConvDim] = 2

		# print(inputShape, filterShape)
		assert (inputShape[1] == filterShape[1])
		# For Input:
		# [N, CI, H, W] is the Onnx order it should be changed to 
		# [N, H, W, CI] order 
		reshaped_input_name = get_new_var_name(out_var_count)
		reshaped_input = get_reshaped_input_ast(inputsRef[0], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input, reshaped_input_name, mtdAST)
		out_var_count += 1

		# For filter:
		# [CO, CI1, FH, FW] is the Onnx order it should be changed to 
		# [FH, FW, CI1, CO] order
		reshaped_filter_name = get_new_var_name(out_var_count)
		reshaped_filter = get_reshaped_filter_ast(inputsRef[1], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_filter, reshaped_filter_name, mtdAST)
		out_var_count += 1

		seedot_output_ast =  AST.BOp(AST.ID(reshaped_input_name), getOperatorsIdx('#'), AST.ID(reshaped_filter_name), options)
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		# If there is bias to be added then reshape and add it 
		if (len(inputsRef) == 3):
			reshaped_bias_name = get_new_var_name(out_var_count)
			reshaped_bias = get_reshaped_bias_ast(inputsRef[2], value_info, node_name_to_out_var_dict, 2)
			innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_bias, reshaped_bias_name, mtdAST)
			out_var_count += 1	

			seedot_output_ast =  AST.BOp(AST.ID(output_name), getOperatorsIdx('+'), AST.ID(reshaped_bias_name), options)
			output_name = get_new_var_name(out_var_count)
			innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
			out_var_count += 1

		return (innermost_let_ast_node, out_var_count, output_name)

	def conv3d(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		inputsRef = node.inputs
		inputShape = value_info[inputsRef[0]][1]
		filterShape = value_info[inputsRef[1]][1]
		stridesUsed = node.attrs['strides']

		assert(len(inputsRef)==2 or len(inputsRef)==3)
		assert(len(stridesUsed)==3)
		assert(value_info[node.inputs[1]][1][2:] == tuple(node.attrs['kernel_shape']))
		# verify this order
		[zPadDLeft, zPadDRight, zPadHLeft, zPadHRight, zPadWLeft, zPadWRight] = node.attrs['pads']

		options = {}
		options[AST.PaddingKeysDict.FD] = filterShape[2]
		options[AST.PaddingKeysDict.FH] = filterShape[3]
		options[AST.PaddingKeysDict.FW] = filterShape[4]
		options[AST.PaddingKeysDict.zPadDLeft] = zPadDLeft
		options[AST.PaddingKeysDict.zPadDRight] = zPadDRight
		options[AST.PaddingKeysDict.zPadHLeft] = zPadHLeft
		options[AST.PaddingKeysDict.zPadHRight] = zPadHRight
		options[AST.PaddingKeysDict.zPadWLeft] = zPadWLeft
		options[AST.PaddingKeysDict.zPadWRight] = zPadWRight
		options[AST.PaddingKeysDict.strideD] = stridesUsed[0]
		options[AST.PaddingKeysDict.strideH] = stridesUsed[1]
		options[AST.PaddingKeysDict.strideW] = stridesUsed[2]
		options[AST.PaddingKeysDict.ConvDim] = 3

		assert (inputShape[1] == filterShape[1])
		# For Input:
		# [N, CI, D, H, W] is the Onnx order it should be changed to 
		# [N, D, H, W, CI] order 
		reshaped_input_name = get_new_var_name(out_var_count)
		reshaped_input = get_reshaped_input_ast(inputsRef[0], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input, reshaped_input_name, mtdAST)
		out_var_count += 1

		# For filter:
		# [CO, CI1, FD, FH, FW] is the Onnx order it should be changed to 
		# [FD, FH, FW, CI1, CO] order
		reshaped_filter_name = get_new_var_name(out_var_count)
		reshaped_filter = get_reshaped_filter_ast(inputsRef[1], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_filter, reshaped_filter_name, mtdAST)
		out_var_count += 1

		seedot_output_ast =  AST.BOp(AST.ID(reshaped_input_name), getOperatorsIdx('#'), AST.ID(reshaped_filter_name), options)
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		# If there is bias to be added then reshape and add it 
		if (len(inputsRef) == 3):
			reshaped_bias_name = get_new_var_name(out_var_count)
			reshaped_bias = get_reshaped_bias_ast(inputsRef[2], value_info, node_name_to_out_var_dict, 3)
			innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_bias, reshaped_bias_name, mtdAST)
			out_var_count += 1	

			seedot_output_ast =  AST.BOp(AST.ID(output_name), getOperatorsIdx('+'), AST.ID(reshaped_bias_name), options)
			output_name = get_new_var_name(out_var_count)
			innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
			out_var_count += 1

		return (innermost_let_ast_node, out_var_count, output_name)

	def MaxPool(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		return ONNXNodesAST.helper_processPool(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST, 'MAXPOOL')

	def AvgPool(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		return ONNXNodesAST.helper_processPool(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST, 'AVGPOOL')

	def GlobalAveragePool(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 
		if(DEBUG):
			print(node)
		inputsRef = node.inputs
		assert(len(inputsRef)==1)

		reshaped_input_name = get_new_var_name(out_var_count)
		reshaped_input = get_reshaped_input_ast(inputsRef[0], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input, reshaped_input_name, mtdAST)
		out_var_count += 1

		seedot_output_ast = AST.Pool(AST.Pool.PoolType.AvgPool,
							  AST.ID(reshaped_input_name),
							  {
							  	AST.PaddingKeysDict.FH: value_info[inputsRef[0]][1][2],
							  	AST.PaddingKeysDict.FW: value_info[inputsRef[0]][1][3],
							  	AST.PaddingKeysDict.zPadHLeft: 0,
							  	AST.PaddingKeysDict.zPadHRight: 0,
							  	AST.PaddingKeysDict.zPadWLeft: 0,
							  	AST.PaddingKeysDict.zPadWRight: 0,
							  	AST.PaddingKeysDict.strideH: 1,
							  	AST.PaddingKeysDict.strideW: 1
							  }
							)	
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		reshaped_output_name = get_new_var_name(out_var_count)
		onnx_output_ast = get_reshaped_output_ast(node.outputs[0], value_info, output_name)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, onnx_output_ast, reshaped_output_name, mtdAST)	
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = reshaped_output_name
		
		return (innermost_let_ast_node, out_var_count)

	def helper_processPool(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST, typeOfPool):
		node = OnnxNode(node) 
		if(DEBUG):
			print(node)
		inputsRef = node.inputs
		assert(len(inputsRef)==1)
				
		stridesUsed = node.attrs['strides']
		strideH = stridesUsed[0]
		strideW = stridesUsed[1]

		kSizeUsed = node.attrs['kernel_shape']
		# assert((kSizeUsed[0] == 1) and (kSizeUsed[3] == 1))
		kSizeH = kSizeUsed[0]
		kSizeW = kSizeUsed[1]
		
		inputShape = value_info[inputsRef[0]][1]
		# print(inputShape)
		imgH = inputShape[2]
		imgW = inputShape[3]

		# verify order
		[zPadHLeft, zPadHRight, zPadWLeft, zPadWRight] = node.attrs['pads']


		reshaped_input_name = get_new_var_name(out_var_count)
		reshaped_input = get_reshaped_input_ast(inputsRef[0], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input, reshaped_input_name, mtdAST)
		out_var_count += 1

		poolType = None
		if typeOfPool=='MAXPOOL': poolType = AST.Pool.PoolType.MaxPool
		elif typeOfPool=='AVGPOOL': poolType = AST.Pool.PoolType.AvgPool
		else: 
			print("Unknown type of pooling layer.", file=sys.stderr)
			assert(False)
		seedot_output_ast = AST.Pool(poolType,
							  AST.ID(reshaped_input_name),
							  {
							  	AST.PaddingKeysDict.FH: kSizeH,
							  	AST.PaddingKeysDict.FW: kSizeW,
							  	AST.PaddingKeysDict.zPadHLeft: zPadHLeft,
							  	AST.PaddingKeysDict.zPadHRight: zPadHRight,
							  	AST.PaddingKeysDict.zPadWLeft: zPadWLeft,
							  	AST.PaddingKeysDict.zPadWRight: zPadWRight,
							  	AST.PaddingKeysDict.strideH: strideH,
							  	AST.PaddingKeysDict.strideW: strideW
							  }
							)
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1


		reshaped_output_name = get_new_var_name(out_var_count)
		onnx_output_ast = get_reshaped_output_ast(node.outputs[0], value_info, output_name)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, onnx_output_ast, reshaped_output_name, mtdAST)	
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = reshaped_output_name
		
		return (innermost_let_ast_node, out_var_count)

	def ConvTranspose(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		node = OnnxNode(node) 
		if(DEBUG):
			print(node)

		inputsRef = node.inputs
		# since two dimensions represent N: Number of batches and CI: Input channel
		inputShape = value_info[inputsRef[0]][1]
		spatial_size = len(inputShape)-2
		if spatial_size == 2:
			(innermost_let_ast_node, out_var_count, output_name) = ONNXNodesAST.conv2dtranspose(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST)
		elif spatial_size == 3:
			(innermost_let_ast_node, out_var_count, output_name) = ONNXNodesAST.conv3dtranspose(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST)	

		reshaped_output_name = get_new_var_name(out_var_count)
		onnx_output_ast = get_reshaped_output_ast(node.outputs[0],value_info, output_name)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, onnx_output_ast, reshaped_output_name, mtdAST)
		out_var_count += 1
		node_name_to_out_var_dict[node.outputs[0]] = reshaped_output_name

		return (innermost_let_ast_node, out_var_count)

	def conv2dtranspose(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		inputsRef = node.inputs
		inputShape = value_info[inputsRef[0]][1]
		filterShape = value_info[inputsRef[1]][1]
		stridesUsed = node.attrs['strides']
		outputShape = value_info[node.outputs[0]][1]

		# sometimes there is a bias to be added as well		
		assert(len(inputsRef)==2 or len(inputsRef)==3)
		assert(len(stridesUsed)==2)
		assert(value_info[node.inputs[1]][1][2:] == tuple(node.attrs['kernel_shape']))
		# verify this order
		[zPadHLeft, zPadHRight, zPadWLeft, zPadWRight] = node.attrs['pads']

		options = {}
		options[AST.PaddingKeysDict.FH] = filterShape[2]
		options[AST.PaddingKeysDict.FW] = filterShape[3]
		options[AST.PaddingKeysDict.zPadHLeft] = zPadHLeft
		options[AST.PaddingKeysDict.zPadHRight] = zPadHRight
		options[AST.PaddingKeysDict.zPadWLeft] = zPadWLeft
		options[AST.PaddingKeysDict.zPadWRight] = zPadWRight
		options[AST.PaddingKeysDict.strideH] = stridesUsed[0]
		options[AST.PaddingKeysDict.strideW] = stridesUsed[1]
		options[AST.PaddingKeysDict.ConvDim] = 2		
		options[AST.PaddingKeysDict.outputImgH] = outputShape[2]
		options[AST.PaddingKeysDict.outputImgW] = outputShape[3]

		assert (inputShape[1] == filterShape[0])
		# For Input:
		# [N, CI, H, W] is the Onnx order it should be changed to 
		# [N, H, W, CI] order 

		reshaped_input_name = get_new_var_name(out_var_count)
		reshaped_input = get_reshaped_input_ast(inputsRef[0], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input, reshaped_input_name, mtdAST)
		out_var_count += 1
		# For filter:
		# [CI, CO, FH, FW] is the Onnx order it should be changed to 
		# [FH, FW, CI1, CO] order
		reshaped_filter_name = get_new_var_name(out_var_count)
		reshaped_filter = get_reshaped_filter_ast(inputsRef[1], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_filter, reshaped_filter_name, mtdAST)
		out_var_count += 1

		seedot_output_ast =  AST.BOp(AST.ID(reshaped_input_name), getOperatorsIdx('#T'), AST.ID(reshaped_filter_name), options)
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		# If there is bias to be added then reshape and add it 
		if (len(inputsRef) == 3):
			biasShape = value_info[inputsRef[2]][1]
			reshaped_bias_name = get_new_var_name(out_var_count)
			reshaped_bias = get_reshaped_bias_ast(inputsRef[2], value_info, node_name_to_out_var_dict, 2)
			innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_bias, reshaped_bias_name, mtdAST)
			out_var_count += 1	

			seedot_output_ast =  AST.BOp(AST.ID(output_name), getOperatorsIdx('+'), AST.ID(reshaped_bias_name), options)
			output_name = get_new_var_name(out_var_count)
			innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
			out_var_count += 1

		return (innermost_let_ast_node, out_var_count, output_name)	

	def conv3dtranspose(node, value_info, node_name_to_out_var_dict, innermost_let_ast_node, out_var_count, mtdAST):
		inputsRef = node.inputs
		inputShape = value_info[inputsRef[0]][1]
		filterShape = value_info[inputsRef[1]][1]
		stridesUsed = node.attrs['strides']
		outputShape = value_info[node.outputs[0]][1]

		# sometimes there is a bias to be added as well		
		assert(len(inputsRef)==2 or len(inputsRef)==3)
		assert(len(stridesUsed)==3)
		assert(value_info[node.inputs[1]][1][2:] == tuple(node.attrs['kernel_shape']))
		# verify this order
		[zPadDLeft, zPadDRight, zPadHLeft, zPadHRight, zPadWLeft, zPadWRight] = node.attrs['pads']

		options = {}
		options[AST.PaddingKeysDict.FD] = filterShape[2]
		options[AST.PaddingKeysDict.FH] = filterShape[3]
		options[AST.PaddingKeysDict.FW] = filterShape[4]
		options[AST.PaddingKeysDict.zPadDLeft] = zPadDLeft
		options[AST.PaddingKeysDict.zPadDRight] = zPadDRight
		options[AST.PaddingKeysDict.zPadHLeft] = zPadHLeft
		options[AST.PaddingKeysDict.zPadHRight] = zPadHRight
		options[AST.PaddingKeysDict.zPadWLeft] = zPadWLeft
		options[AST.PaddingKeysDict.zPadWRight] = zPadWRight
		options[AST.PaddingKeysDict.strideD] = stridesUsed[0]
		options[AST.PaddingKeysDict.strideH] = stridesUsed[1]
		options[AST.PaddingKeysDict.strideW] = stridesUsed[2]
		options[AST.PaddingKeysDict.ConvDim] = 3		
		options[AST.PaddingKeysDict.outputImgD] = outputShape[2]
		options[AST.PaddingKeysDict.outputImgH] = outputShape[3]
		options[AST.PaddingKeysDict.outputImgW] = outputShape[4]

		assert (inputShape[1] == filterShape[0])
		# For Input:
		# [N, CI, D, H, W] is the Onnx order it should be changed to 
		# [N, D, H, W, CI] order 

		reshaped_input_name = get_new_var_name(out_var_count)
		reshaped_input = get_reshaped_input_ast(inputsRef[0], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_input, reshaped_input_name, mtdAST)
		out_var_count += 1
		# For filter:
		# [CI, CO, FD, FH, FW] is the Onnx order it should be changed to 
		# [FD, FH, FW, CI1, CO] order
		reshaped_filter_name = get_new_var_name(out_var_count)
		reshaped_filter = get_reshaped_filter_ast(inputsRef[1], value_info, node_name_to_out_var_dict)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_filter, reshaped_filter_name, mtdAST)
		out_var_count += 1

		seedot_output_ast =  AST.BOp(AST.ID(reshaped_input_name), getOperatorsIdx('#T'), AST.ID(reshaped_filter_name), options)
		output_name = get_new_var_name(out_var_count)
		innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
		out_var_count += 1

		# If there is bias to be added then reshape and add it 
		if (len(inputsRef) == 3):
			biasShape = value_info[inputsRef[2]][1]
			reshaped_bias_name = get_new_var_name(out_var_count)
			reshaped_bias = get_reshaped_bias_ast(inputsRef[2], value_info, node_name_to_out_var_dict, 3)
			innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, reshaped_bias, reshaped_bias_name, mtdAST)
			out_var_count += 1	

			seedot_output_ast =  AST.BOp(AST.ID(output_name), getOperatorsIdx('+'), AST.ID(reshaped_bias_name), options)
			output_name = get_new_var_name(out_var_count)
			innermost_let_ast_node = update_program_with_new_node(innermost_let_ast_node, seedot_output_ast, output_name, mtdAST)
			out_var_count += 1



		return (innermost_let_ast_node, out_var_count, output_name)
		