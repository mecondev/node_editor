"""
Edge Validators - Validation functions for edge connections.

This module provides validation callback functions that can be registered
to the Edge class to validate edge connections.

Example usage:
    from node_editor.tools.edge_validators import *
    
    Edge.registerEdgeValidator(edge_cannot_connect_two_outputs_or_two_inputs)
    Edge.registerEdgeValidator(edge_cannot_connect_input_and_output_of_same_node)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from node_editor.core.socket import Socket

DEBUG = False


def print_error(*args) -> None:
    """Helper function for printing validation errors.
    
    Args:
        *args: Arguments to print
    """
    if DEBUG:
        print("Edge Validation Error:", *args)


def edge_validator_debug(input_socket: Socket, output_socket: Socket) -> bool:
    """Debug validator that always returns True but prints debug info.
    
    Args:
        input_socket: Input socket
        output_socket: Output socket
        
    Returns:
        Always True
    """
    print("VALIDATING:")
    print(
        input_socket,
        "input" if input_socket.is_input else "output",
        "of node", input_socket.node
    )
    for s in input_socket.node.inputs + input_socket.node.outputs:
        print("\t", s, "input" if s.is_input else "output")
    
    print(
        output_socket,
        "input" if output_socket.is_input else "output",
        "of node", output_socket.node
    )
    for s in output_socket.node.inputs + output_socket.node.outputs:
        print("\t", s, "input" if s.is_input else "output")
    
    return True


def edge_cannot_connect_two_outputs_or_two_inputs(
    input_socket: Socket, output_socket: Socket
) -> bool:
    """Validate that edge doesn't connect two outputs or two inputs.
    
    Args:
        input_socket: First socket
        output_socket: Second socket
        
    Returns:
        True if connection is valid
    """
    if input_socket.is_output and output_socket.is_output:
        print_error("Connecting 2 outputs")
        return False
    
    if input_socket.is_input and output_socket.is_input:
        print_error("Connecting 2 inputs")
        return False
    
    return True


def edge_cannot_connect_input_and_output_of_same_node(
    input_socket: Socket, output_socket: Socket
) -> bool:
    """Validate that edge doesn't connect the same node to itself.
    
    Args:
        input_socket: First socket
        output_socket: Second socket
        
    Returns:
        True if connection is valid
    """
    if input_socket.node == output_socket.node:
        print_error("Connecting the same node")
        return False
    
    return True


def edge_cannot_connect_input_and_output_of_different_type(
    input_socket: Socket, output_socket: Socket
) -> bool:
    """Validate that edge connects sockets of the same type (color).
    
    Args:
        input_socket: First socket
        output_socket: Second socket
        
    Returns:
        True if connection is valid
    """
    if input_socket.socket_type != output_socket.socket_type:
        print_error("Connecting sockets with different colors")
        return False
    
    return True
