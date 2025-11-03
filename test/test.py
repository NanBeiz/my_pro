import sys


def parse_matrix(text: str):
    """Parse a matrix from a string.

    Accepts rows separated by ';' or newlines. Columns separated by spaces or commas.
    Example inputs:
      "1 2; 3 4"
      "1,2;3,4"
      "1 2 3\n4 5 6"
    """
    if not text.strip():
        raise ValueError("Empty matrix input")
    if ";" in text:
        rows_raw = [r.strip() for r in text.strip().split(";")]
    else:
        rows_raw = [r.strip() for r in text.strip().splitlines()]
    matrix = []
    width = None
    for row in rows_raw:
        if not row:
            continue
        # Split by comma or whitespace
        parts = [p for token in row.split(',') for p in token.split()] if "," in row else row.split()
        try:
            nums = [float(p) for p in parts]
        except ValueError as exc:
            raise ValueError(f"Invalid number in row '{row}': {exc}") from exc
        if width is None:
            width = len(nums)
            if width == 0:
                raise ValueError("Row has no elements")
        elif len(nums) != width:
            raise ValueError("Inconsistent row lengths in matrix")
        matrix.append(nums)
    if not matrix:
        raise ValueError("No rows parsed for matrix")
    return matrix


def shape_of(matrix):
    return (len(matrix), len(matrix[0]) if matrix else 0)


def require_same_shape(a, b):
    sa, sb = shape_of(a), shape_of(b)
    if sa != sb:
        raise ValueError(f"Shape mismatch: {sa} vs {sb}")


def add_matrices(a, b):
    require_same_shape(a, b)
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def subtract_matrices(a, b):
    require_same_shape(a, b)
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def multiply_matrices(a, b):
    n, k_a = shape_of(a)
    k_b, m = shape_of(b)
    if k_a != k_b:
        # a is n x k, b is k x m
        if len(a[0]) != len(b):
            raise ValueError(f"Inner dimensions do not match: {shape_of(a)} * {shape_of(b)}")
    result = [[0.0 for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for k in range(len(b)):
            aik = a[i][k]
            if aik == 0:
                continue
            for j in range(m):
                result[i][j] += aik * b[k][j]
    return result


def transpose_matrix(a):
    rows, cols = shape_of(a)
    return [[a[i][j] for i in range(rows)] for j in range(cols)]


def determinant(a):
    n, m = shape_of(a)
    if n != m:
        raise ValueError("Determinant is defined only for square matrices")
    # Use Gaussian elimination with partial pivoting
    mat = [row[:] for row in a]
    det = 1.0
    for col in range(n):
        # Find pivot
        pivot_row = max(range(col, n), key=lambda r: abs(mat[r][col]))
        pivot = mat[pivot_row][col]
        if abs(pivot) < 1e-12:
            return 0.0
        if pivot_row != col:
            mat[col], mat[pivot_row] = mat[pivot_row], mat[col]
            det *= -1.0
        det *= mat[col][col]
        # Eliminate below
        for r in range(col + 1, n):
            factor = mat[r][col] / mat[col][col]
            if abs(factor) < 1e-18:
                continue
            for c in range(col, n):
                mat[r][c] -= factor * mat[col][c]
    return det


def inverse(a):
    n, m = shape_of(a)
    if n != m:
        raise ValueError("Inverse is defined only for square matrices")
    # Augment with identity and perform Gauss-Jordan
    mat = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(a)]
    # Forward elimination
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(mat[r][col]))
        pivot = mat[pivot_row][col]
        if abs(pivot) < 1e-12:
            raise ValueError("Matrix is singular and cannot be inverted")
        if pivot_row != col:
            mat[col], mat[pivot_row] = mat[pivot_row], mat[col]
        # Normalize pivot row
        pivot_val = mat[col][col]
        for c in range(2 * n):
            mat[col][c] /= pivot_val
        # Eliminate other rows
        for r in range(n):
            if r == col:
                continue
            factor = mat[r][col]
            if abs(factor) < 1e-18:
                continue
            for c in range(2 * n):
                mat[r][c] -= factor * mat[col][c]
    inv = [row[n:] for row in mat]
    return inv


def format_matrix(a):
    # Pretty print with minimal trailing zeros
    def fmt(x):
        if abs(x) < 1e-12:
            x = 0.0
        s = f"{x:.10f}".rstrip('0').rstrip('.')
        return s if s else "0"
    widths = []
    for j in range(len(a[0])):
        col_width = max(len(fmt(a[i][j])) for i in range(len(a)))
        widths.append(col_width)
    lines = []
    for i in range(len(a)):
        parts = [fmt(a[i][j]).rjust(widths[j]) for j in range(len(a[0]))]
        lines.append("[ " + "  ".join(parts) + " ]")
    return "\n".join(lines)


def read_matrix_from_stdin(prompt: str):
    print(prompt)
    print("请输入矩阵，行用 ';' 或换行分隔，列用空格或逗号分隔：")
    print("例如: 1 2; 3 4  或  1,2,3\n      4,5,6")
    print("输入结束后按回车确认。")
    lines = []
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
        if line == "":
            # empty line indicates end for multi-line input
            break
        lines.append(line)
        if ";" in line:
            # likely single-line style; break after first line
            break
    text = "\n".join(lines)
    return parse_matrix(text)


def main():
    menu = (
        "矩阵计算器 — 请选择操作:\n"
        "1) 加法 A + B\n"
        "2) 减法 A - B\n"
        "3) 乘法 A × B\n"
        "4) 转置 A^T\n"
        "5) 行列式 det(A)\n"
        "6) 逆矩阵 A^{-1}\n"
        "0) 退出\n"
    )
    while True:
        print(menu)
        choice = input("输入编号: ").strip()
        if choice == "0":
            print("已退出。")
            return
        try:
            if choice == "1":
                a = read_matrix_from_stdin("输入矩阵 A：")
                b = read_matrix_from_stdin("输入矩阵 B：")
                c = add_matrices(a, b)
                print("结果:\n" + format_matrix(c))
            elif choice == "2":
                a = read_matrix_from_stdin("输入矩阵 A：")
                b = read_matrix_from_stdin("输入矩阵 B：")
                c = subtract_matrices(a, b)
                print("结果:\n" + format_matrix(c))
            elif choice == "3":
                a = read_matrix_from_stdin("输入矩阵 A：")
                b = read_matrix_from_stdin("输入矩阵 B：")
                c = multiply_matrices(a, b)
                print("结果:\n" + format_matrix(c))
            elif choice == "4":
                a = read_matrix_from_stdin("输入矩阵 A：")
                t = transpose_matrix(a)
                print("结果 A^T:\n" + format_matrix(t))
            elif choice == "5":
                a = read_matrix_from_stdin("输入矩阵 A：")
                d = determinant(a)
                print(f"det(A) = {d}")
            elif choice == "6":
                a = read_matrix_from_stdin("输入矩阵 A：")
                inv = inverse(a)
                print("A^{-1}：\n" + format_matrix(inv))
            else:
                print("无效选项，请重试。")
        except Exception as exc:
            print(f"错误: {exc}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)


