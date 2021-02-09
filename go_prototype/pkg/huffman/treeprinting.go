package huffman

import "fmt"

func printT(node *Node, isLeft bool, offset int, depth int, s *[][]rune) int {
	var b string
	width := 3

	if node == nil { return 0 }

	if node.left == nil && node.right == nil {
		b = fmt.Sprintf("(%s)", node.value[0])
	} else {
		b = " | "
	}

	left := printT(node.left, true, offset, depth + 1, s)
	right := printT(node.right, false, offset + left + width, depth + 1, s)

	for i := 0; i < width; i++ {
		(*s)[2 * depth][offset + left + i] = rune(b[i])
	}

	if depth != 0 && isLeft {
		for i := 0; i < width + right; i++ {
			(*s)[2 * depth - 1][offset + left + width/2 + i] = '-'
		}

		(*s)[2 * depth - 1][offset + left + width/2] = '+'
		(*s)[2 * depth - 1][offset + left + width + right + width/2] = '+'
	} else if depth != 0 && !isLeft {
		for i := 0; i < left + width; i++ {
			(*s)[2 * depth - 1][offset - width/2 + i] = '-'
		}

		// printing the end of the branch
		(*s)[2 * depth - 1][offset + left + width/2] = '+'
		(*s)[2 * depth - 1][offset - width/2 - 1] = '+'
	}

	return left + width + right
}

func PrintTree(root *Node) {
	width := 120

	s := make([][]rune, 20)
	for i := 0; i < len(s); i++ {
		s[i] = make([]rune, width)
		for j := 0; j < width; j++ {
			s[i][j] = ' '
		}
	}

	printT(root, false, 0, 0, &s)

	var empty bool
	for i := 0; i < len(s); i++ {
		empty = true

		for c := 0; c < width; c++ {
			if s[i][c] != ' ' {
				empty = false
				break
			}
		}

		if !empty {
			for j := 0; j < width; j++ {
				fmt.Printf("%c", s[i][j])
			}
			fmt.Println()
		}
	}
}