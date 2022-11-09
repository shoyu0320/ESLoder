from typing import List, Optional, TypeVar

import numpy as np

_CellNode = TypeVar("_CellNode", bound="CellNode")
_CellTree = TypeVar("_CellTree", bound="CellTree")


class CellNode:
    def __init__(self,
                 idx: int = 0,
                 child_rate: float = 0.5):
        self.right_children: List[_CellNode] = []
        self.bottom_children: List[_CellNode] = []
        self.left_parents: List[_CellNode] = []
        self.top_parents: List[_CellNode] = []
        self.content = ""
        self.idx = idx
        self.child_rate = child_rate
        self.right_pad: int = 0

    def has_parent(self) -> bool:
        flg: bool = False
        flg |= self.has_top()
        flg |= self.has_left()
        return flg

    def has_child(self) -> bool:
        flg: bool = False
        flg |= self.has_bottom()
        flg |= self.has_right()
        return flg

    def has_right(self) -> bool:
        return len(self.right_children) > 0

    def has_bottom(self) -> bool:
        return len(self.bottom_children) > 0

    def has_top(self) -> bool:
        return len(self.top_parents) > 0

    def has_left(self) -> bool:
        return len(self.left_parents) > 0

    @property
    def height(self) -> int:
        output: int = 0
        if len(self.right_children) == 0:
            return output + 1
        else:
            output += self.right_children[0].height
            for child in self.right_children[1:]:
                if isinstance(child, (int, float)):
                    output += 1
                else:
                    output += child.height
            return output

    @property
    def depth_right(self) -> int:
        output: int = self.width
        if not self.has_right():
            return output
        else:
            child_depth: int = max([child.dept_right for child in self.right_children])
            return output + child_depth

    @property
    def depth_bottom(self) -> int:
        output: int = self.height
        if not self.has_right():
            return output
        else:
            child_depth: int = max([child.depth_bottom for child in self.bottom_children])
            return output + child_depth

    @property
    def width(self) -> int:
        output: int = self.right_pad
        if len(self.bottom_children) == 0:
            return output + 1
        else:
            output += self.bottom_children[0].width
            for child in self.bottom_children[1:]:
                if isinstance(child, (int, float)):
                    output += 1
                else:
                    output += child.width
            return output

    def pad_right(self, max_depth: int = 0, accum_width: int = 0) -> None:
        if not self.has_right():
            self.right_pad: int = max_depth - (accum_width + self.width)
        else:
            for child in self.right_children:
                current_width = accum_width + self.width
                child.pad_right(max_depth, current_width)

    def get_next_list(self, use_dim: int = 0) -> List[int]:
        if use_dim == 0:
            return self.right_children
        elif use_dim == 1:
            return self.bottom_children
        else:
            raise ValueError()

    def add_child(self, cell: int, use_dim: int = 0) -> None:
        next_list = self.get_next_list(use_dim)
        next_list.append(cell)

    def add_parent(self, cell: int, use_dim: int = 0) -> None:
        if use_dim == 0:
            self.left_parents.append(cell)
        elif use_dim == 1:
            self.top_parents.append(cell)
        else:
            raise ValueError()

    def create_idx_specified_array(self, array, idx: Optional[int] = None):
        if idx is None:
            idx = self.idx

        idx_array = np.zeros_like(array, dtype=bool)

        if not (idx > 0):
            return idx_array

        idx_array[array == idx] = True
        return idx_array

    def get_pad(self, size, use_dim: int = 0):
        pad_shape = [1, 1]
        pad_shape[use_dim] = size
        return np.zeros(pad_shape, dtype=bool)

    def shift_data_with_pad(self,
                            array,
                            pad = None,
                            use_dim: int = 0):
        if pad is None:
            size = array.shape[use_dim]
            pad = self.get_pad(size, use_dim)

        if use_dim == 0:
            return np.c_[pad, array[:, :-1]]
        elif use_dim == 1:
            return np.r_[pad, array[:-1, :]]
        else:
            raise ValueError()

    def get_edge_cells(self, array, pad = None, use_dim: int = 0, idx: Optional[int] = None):
        frame = self.create_idx_specified_array(array, idx)
        if (np.sum(frame) == 0) and (idx > 0):
            raise ValueError(
                "One True flag should be exist at least in an frame array, "
                f"but no {idx} is included in the array."
            )

        shifted_frame = self.shift_data_with_pad(frame, use_dim=use_dim)
        if idx is None:
            return shifted_frame * ~frame
        else:
            return ~shifted_frame * frame

    def get_next_cells(self, array, use_dim: int = 0):
        edge_cells = self.get_edge_cells(array, use_dim=use_dim)
        return array[edge_cells].astype(int)

    def calc_next_rate_by_cell(self, array, next_cells, cell_idx: int, use_dim: int = 0):
        if not (cell_idx > 0):
            return 0
        edge_cells = self.get_edge_cells(array, use_dim=use_dim, idx=cell_idx)
        count_in_array = np.sum(edge_cells)
        count_in_next = np.sum(next_cells == cell_idx)
        if count_in_next > count_in_array:
            raise ValueError("数デカすぎ")
        return count_in_next / count_in_array

    def find_next_cells(self, array, use_dim: int = 0, tree = {}):
        next_cells = self.get_next_cells(array, use_dim=use_dim)
        next_uniques = np.unique(next_cells)

        for cell in next_uniques:
            next_rate = self.calc_next_rate_by_cell(array, next_cells, cell, use_dim=use_dim)

            if next_rate > self.child_rate:
                self.add_child(tree.get(cell, cell), use_dim)


class CellTree:
    @classmethod
    def create_tree(cls, array, child_rate: float = 0.5) -> _CellTree:
        tree = cls(array, child_rate)
        tree.make_graph()
        tree.normalize_cells()
        return tree

    def __init__(self, excel_array, child_rate: float = 0.5):
        self.excel_array = excel_array.astype(int)
        self.child_rate = child_rate
        self.tree: dict[int, CellNode] = {}

    def make_nodes(self, unique_idx: List[int]) -> None:
        for idx in unique_idx:
            self.tree[idx] = CellNode(idx, self.child_rate)

    def normalize_cells(self) -> None:
        # TODO 深さ探索して最深までの階層をちゃんと出す
        roots: dict[int, CellNode] = self.get_roots()
        print(roots)
        max_in_block: int
        for idx, node in roots.items():
            max_in_block = node.depth_right
            node.pad_right(max_in_block)

    def get_roots(self) -> dict[int, CellNode]:
        output: dict[int, CellNode] = {}
        for idx, node in self.tree.items():
            if not node.has_parent:
                output[idx] = node
        return output

    def make_edges(self, use_dim: int = 0) -> None:
        for idx, node in self.tree.items():
            if idx < 0:
                continue
            node.find_next_cells(self.excel_array,
                                 use_dim=use_dim,
                                 tree=self.tree)

            children = node.get_next_list(use_dim)
            for child in children:
                self.tree[child.idx].add_parent(node, use_dim=use_dim)

    def make_graph(self) -> None:
        idx_unique = np.unique(
            self.excel_array.astype(int)).tolist()
        self.make_nodes(idx_unique)
        self.make_edges(use_dim=0)
        self.make_edges(use_dim=1)
