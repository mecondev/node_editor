"""
Scene History - Undo/Redo functionality.

This module provides history management for the node editor, allowing
users to undo and redo operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from node_editor.core.scene import Scene

DEBUG = False
DEBUG_SELECTION = False


class SceneHistory:
    """Class managing undo/redo operations for a Scene.
    
    The history system works by storing serialized snapshots of the scene
    at different points in time. Each snapshot includes the scene state
    and the current selection.
    
    Attributes:
        scene: Reference to the Scene being managed
        history_limit: Maximum number of history steps to store (default: 32)
        history_stack: List of history stamps
        history_current_step: Current position in the history stack
        undo_selection_has_changed: Flag indicating if selection changed after undo
    """
    
    def __init__(self, scene: Scene) -> None:
        """Initialize history for a scene.
        
        Args:
            scene: Scene instance to manage history for
        """
        self.scene = scene
        
        # History stack
        self.history_stack: list[dict] = []
        self.history_current_step: int = -1
        self.history_limit: int = 32
        
        # Selection tracking
        self.undo_selection_has_changed: bool = False
        
        # Event listeners
        self._history_modified_listeners: list[Callable] = []
        self._history_stored_listeners: list[Callable] = []
        self._history_restored_listeners: list[Callable] = []
    
    def clear(self) -> None:
        """Reset the history stack."""
        self.history_stack = []
        self.history_current_step = -1
    
    def storeInitialHistoryStamp(self) -> None:
        """Store initial history stamp.
        
        Helper function usually used when new or open file is requested.
        """
        self.storeHistory("Initial History Stamp")
    
    # Event listener management
    
    def addHistoryModifiedListener(self, callback: Callable) -> None:
        """Register callback for 'History Modified' event.
        
        Args:
            callback: Function to call when history is modified
        """
        self._history_modified_listeners.append(callback)
    
    def addHistoryStoredListener(self, callback: Callable) -> None:
        """Register callback for 'History Stored' event.
        
        Args:
            callback: Function to call when history is stored
        """
        self._history_stored_listeners.append(callback)
    
    def addHistoryRestoredListener(self, callback: Callable) -> None:
        """Register callback for 'History Restored' event.
        
        Args:
            callback: Function to call when history is restored
        """
        self._history_restored_listeners.append(callback)
    
    def removeHistoryStoredListener(self, callback: Callable) -> None:
        """Remove registered callback for 'History Stored' event.
        
        Args:
            callback: Function to remove
        """
        if callback in self._history_stored_listeners:
            self._history_stored_listeners.remove(callback)
    
    def removeHistoryRestoredListener(self, callback: Callable) -> None:
        """Remove registered callback for 'History Restored' event.
        
        Args:
            callback: Function to remove
        """
        if callback in self._history_restored_listeners:
            self._history_restored_listeners.remove(callback)
    
    # Undo/Redo capabilities
    
    def canUndo(self) -> bool:
        """Check if undo is available.
        
        Returns:
            True if undo is available
        """
        return self.history_current_step > 0
    
    def canRedo(self) -> bool:
        """Check if redo is available.
        
        Returns:
            True if redo is available
        """
        return self.history_current_step + 1 < len(self.history_stack)
    
    # Undo/Redo operations
    
    def undo(self) -> None:
        """Perform undo operation."""
        if DEBUG:
            print("UNDO")
        
        if self.canUndo():
            self.history_current_step -= 1
            self.restoreHistory()
            self.scene.has_been_modified = True
    
    def redo(self) -> None:
        """Perform redo operation."""
        if DEBUG:
            print("REDO")
        
        if self.canRedo():
            self.history_current_step += 1
            self.restoreHistory()
            self.scene.has_been_modified = True
    
    # History management
    
    def storeHistory(self, desc: str, setModified: bool = False) -> None:
        """Store current state to history stack.
        
        Args:
            desc: Description of the history stamp
            setModified: If True, mark scene as modified
            
        Triggers:
            - History Modified event
            - History Stored event
        """
        if setModified:
            self.scene.has_been_modified = True
        
        if DEBUG:
            print(f'Storing history "{desc}" .... current_step: @{self.history_current_step} ({len(self.history_stack)})')
        
        # If pointer is not at the end, truncate future history
        if self.history_current_step + 1 < len(self.history_stack):
            self.history_stack = self.history_stack[0:self.history_current_step + 1]
        
        # If history exceeds limit, remove oldest entry
        if self.history_current_step + 1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1
        
        # Create and store history stamp
        hs = self.createHistoryStamp(desc)
        self.history_stack.append(hs)
        self.history_current_step += 1
        
        if DEBUG:
            print(f"  -- setting step to: {self.history_current_step}")
        
        # Trigger listeners
        for callback in self._history_modified_listeners:
            callback()
        for callback in self._history_stored_listeners:
            callback()
    
    def restoreHistory(self) -> None:
        """Restore history stamp from history stack.
        
        Triggers:
            - History Modified event
            - History Restored event
        """
        if DEBUG:
            print(f"Restoring history .... current_step: @{self.history_current_step} ({len(self.history_stack)})")
        
        self.restoreHistoryStamp(self.history_stack[self.history_current_step])
        
        for callback in self._history_modified_listeners:
            callback()
        for callback in self._history_restored_listeners:
            callback()
    
    # History stamp creation and restoration
    
    def captureCurrentSelection(self) -> dict:
        """Capture current selection of nodes and edges.
        
        Returns:
            Dictionary with 'nodes' and 'edges' lists containing IDs
        """
        sel_obj = {
            'nodes': [],
            'edges': [],
        }
        
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_obj['nodes'].append(item.node.id)
            elif hasattr(item, 'edge'):
                sel_obj['edges'].append(item.edge.id)
        
        return sel_obj
    
    def createHistoryStamp(self, desc: str) -> dict:
        """Create a history stamp.
        
        Internally serializes the whole scene and current selection.
        
        Args:
            desc: Descriptive label for the history stamp
            
        Returns:
            Dictionary with scene snapshot and selection
        """
        history_stamp = {
            'desc': desc,
            'snapshot': self.scene.serialize(),
            'selection': self.captureCurrentSelection(),
        }
        
        return history_stamp
    
    def restoreHistoryStamp(self, history_stamp: dict) -> None:
        """Restore a history stamp to the current scene.
        
        Args:
            history_stamp: History stamp to restore
        """
        if DEBUG:
            print(f"RHS: {history_stamp['desc']}")
        
        try:
            self.undo_selection_has_changed = False
            previous_selection = self.captureCurrentSelection()
            
            if DEBUG_SELECTION:
                print(f"selected nodes before restore: {previous_selection['nodes']}")
            
            # Deserialize scene
            self.scene.deserialize(history_stamp['snapshot'])
            
            # Restore edge selection
            for edge in self.scene.edges:
                edge.grEdge.setSelected(False)
            
            for edge_id in history_stamp['selection']['edges']:
                for edge in self.scene.edges:
                    if edge.id == edge_id:
                        edge.grEdge.setSelected(True)
                        break
            
            # Restore node selection
            for node in self.scene.nodes:
                node.grNode.setSelected(False)
            
            for node_id in history_stamp['selection']['nodes']:
                for node in self.scene.nodes:
                    if node.id == node_id:
                        node.grNode.setSelected(True)
                        break
            
            current_selection = self.captureCurrentSelection()
            
            if DEBUG_SELECTION:
                print(f"selected nodes after restore: {current_selection['nodes']}")
            
            # Reset last_selected_items
            self.scene._last_selected_items = self.scene.getSelectedItems()
            
            # Check if selection has changed
            if (current_selection['nodes'] != previous_selection['nodes'] or
                current_selection['edges'] != previous_selection['edges']):
                if DEBUG_SELECTION:
                    print("\nSCENE: Selection has changed")
                self.undo_selection_has_changed = True
        
        except Exception as e:
            from node_editor.utils.helpers import dump_exception
            dump_exception(e)
