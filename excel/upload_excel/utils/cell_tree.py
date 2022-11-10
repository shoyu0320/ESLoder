from typing import Any, List, Optional, TypeVar

import numpy as np

_CellNode = TypeVar("_CellNode", bound="CellNode")
_CellTree = TypeVar("_CellTree", bound="CellTree")


class CellNode:
    def __init__(self,
                 idx: int = 0,
                 child_rate: float = 0.5,
                 content: str = ""):
        self.right_children: List[_CellNode] = []
        self.bottom_children: List[_CellNode] = []
        self.left_parents: List[_CellNode] = []
        self.top_parents: List[_CellNode] = []
        self.content = content
        self.idx = idx
        self.child_rate = child_rate
        self.right_pad: int = 0
        self.temp_width: Optional[bool] = None

    def is_dev_experience(self) -> bool:
        flg = True
        flg &= self.has_top()
        flg &= self.has_right()
        flg &= not self.has_left()
        return flg

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

    def has_right_single(self) -> bool:
        return len(self.right_children) == 1

    def has_right_multi(self) -> bool:
        return len(self.right_children) > 1

    def has_bottom(self) -> bool:
        return len(self.bottom_children) > 0

    def has_bottom_single(self) -> bool:
        return len(self.bottom_children) == 1

    def has_bottom_multi(self) -> bool:
        return len(self.bottom_children) > 1

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
        output: int = self.temp_width
        if not self.has_right():
            return output
        else:
            child_depth: int = max([child.depth_right for child in self.right_children])
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
        if self.temp_width is not None:
            return self.right_pad + self.temp_width

        output: int = self.right_pad
        if self.has_bottom():
            output += self.bottom_children[0].width
            for child in self.bottom_children[1:]:
                if isinstance(child, (int, float)):
                    output += 1
                else:
                    output += child.width
        else:
            output += 1
        self.temp_width = output
        return output

    def get_attribute_messages(self, _attr: str, recurse: bool = True, space_size: int = 0, depth: int = 1) -> str:
        out_list: List[str] = []
        space_size += len(_attr) + 2
        depth -= 1
        txt: str
        attr: List[_CellNode] = getattr(self, _attr)
        for node in attr:
            if recurse and (depth > 0):
                out_list.append(node._helpful_attributes_message(recurse, space_size, depth=depth))
            else:
                txt = str(node.content).replace("\n", "/")
                if len(txt) > 10:
                    txt = txt[:10]
                out_list.append(txt)
        return '\n'.join(out_list)

    def _helpful_attributes_message(self, recurse: bool = True, space: int = 0, depth: int = 1) -> str:
        _space: str = " " * space
        lp: str = self.get_attribute_messages("left_parents", recurse=recurse, space_size=space, depth=depth)
        rc: str = self.get_attribute_messages("right_children", recurse=recurse, space_size=space, depth=depth)
        tp: str = self.get_attribute_messages("top_parents", recurse=recurse, space_size=space, depth=depth)
        bc: str = self.get_attribute_messages("bottom_children", recurse=recurse, space_size=space, depth=depth)
        return (
            "\n"
            f"{_space}Helpful attributes;\n"
            f"{_space}'idx'; {self.idx}\n"
            f"{_space}'right_pad'; {self.right_pad}\n"
            f"{_space}'width'; {self.width}\n"
            f"{_space}'content'; {self.content}\n"
            f"{_space}'left_parents'; {lp}\n"
            f"{_space}'right_children'; {rc}\n"
            f"{_space}'top_parents'; {tp}\n"
            f"{_space}'bottom_children'; {bc}\n"
        )

    def pad_right(self, max_depth: int = 0, accum_width: int = 0) -> None:
        current_width: int = accum_width + self.temp_width
        if current_width > max_depth:
            raise ValueError(
                "'current_width' is a size of accumulated elements of the complete cell block "
                "which is constructed with 'max_depth' pieces of elements.\n"
                "That is why, 'current_width' must have less positive integer value than 'max_depth'.\n"
                f"'current_width'; {current_width}, max_depth; {max_depth}\n"
                f"{self._helpful_attributes_message(depth=3)}"
            )

        if not self.has_right():
            self.right_pad: int = max_depth - current_width
        else:
            for child in self.right_children:
                child.pad_right(max_depth, current_width)

        if self.has_bottom():
            for child in self.bottom_children:
                if not child.has_left():
                    child.pad_right(max_depth, accum_width=accum_width)

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
        if (np.sum(frame) == 0) and (idx > 0 if idx is not None else idx is not None):
            raise ValueError(
                "One True flag should be exist at least in a frame array, "
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
    def create_tree(cls,
                    array,
                    child_rate: float = 0.5,
                    cell_content: dict[int, str] = {}) -> _CellTree:
        tree = cls(array, child_rate)
        tree.make_graph(cell_content)
        tree.normalize_cells()
        return tree

    def __init__(self, excel_array, child_rate: float = 0.5):
        self.excel_array = excel_array.astype(int)
        self.child_rate = child_rate
        self.tree: dict[int, CellNode] = {}

    def make_nodes(self, unique_idx: List[int], cell_content: dict[int, str]) -> None:
        content: Optional[str]
        for idx in unique_idx:
            content = cell_content.get(idx, None)
            self.tree[idx] = CellNode(idx=idx,
                                      child_rate=self.child_rate,
                                      content=content)

    def normalize_cells(self) -> None:
        roots: dict[int, CellNode] = self.get_roots()
        max_in_block: int
        for idx, node in roots.items():
            max_in_block = node.depth_right
            node.pad_right(max_in_block)

    def get_roots(self) -> dict[int, CellNode]:
        output: dict[int, CellNode] = {}
        for idx, node in self.tree.items():
            # temp_widthを作っておく
            node.width
            if not node.has_parent():
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

    def make_graph(self, cell_content: dict[int, str] = {}) -> None:
        idx_unique = np.unique(self.excel_array.astype(int))
        self.make_nodes(idx_unique.tolist(), cell_content)
        self.make_edges(use_dim=0)
        self.make_edges(use_dim=1)
