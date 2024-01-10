        if button == pyglet.window.mouse.LEFT:
            self.set_exclusive()
            self.break_selected_block()

        elif button == pyglet.window.mouse.RIGHT and self.exclusive:
            self.place_block()