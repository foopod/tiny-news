def render_sudoku(puzzle_string, output_file='puzzle.png'):
    from PIL import Image, ImageDraw, ImageFont
    
    size = 575
    image = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(image)
    
    # Calculate cell size
    cell_size = size / 9
    thick_line_width = 4
    thin_line_width = 1
    
    # Draw the grid
    for i in range(10):  # 0 to 9 for 10 lines
        line_width = thick_line_width if i % 3 == 0 else thin_line_width
        pos = i * cell_size
        
        # Vertical lines
        draw.line([(pos, 0), (pos, size)], fill='black', width=line_width)
        # Horizontal lines  
        draw.line([(0, pos), (size, pos)], fill='black', width=line_width)
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", int(cell_size * 0.8))
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", int(cell_size * 0.8))
        except:
            try:
                font = ImageFont.load_default()
                # Make default font bigger by trying to scale it
                font = font.font_variant(size=int(cell_size * 0.5))
            except:
                font = None
    
    # Place numbers
    for i, char in enumerate(puzzle_string):
        if char.isdigit() and char != '0':
            row = i // 9
            col = i % 9
            
            # Calculate position for centering the number
            x = col * cell_size + cell_size / 2
            y = row * cell_size + cell_size / 2
            
            # Draw the number centered in the cell
            if font:
                # Get text bounding box for precise centering
                bbox = draw.textbbox((0, 0), char, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center the text in the cell
                text_x = x - text_width / 2
                text_y = y - text_height / 2
                
                draw.text((text_x, text_y), char, fill='black', font=font)
            else:
                # Fallback with larger offset for bigger appearance
                draw.text((x - cell_size/4, y - cell_size/4), char, fill='black')
    
    # Convert to black and white and save
    bw_image = image.convert('1')
    bw_image.save(output_file)