"""Integration checks with SDL's headless video driver."""
import asyncio
import unittest
from unittest.mock import patch

import pygame
import settings
from game import Game


class MobileTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        pygame.event.clear()

    def tearDown(self):
        pygame.quit()

    def finger(self, kind, finger_id=1, x=0.5, y=0.5):
        pygame.event.post(pygame.event.Event(
            kind, finger_id=finger_id, touch_id=1, x=x, y=y, dx=0, dy=0
        ))
        self.game._handle_events()

    def test_drag_fires_and_release_stops(self):
        self.finger(pygame.FINGERDOWN)
        before = self.game.player.rect.center
        self.finger(pygame.FINGERMOTION, x=0.6, y=0.45)
        self.game.player._last_shot = -1000
        self.game._update()
        after = self.game.player.rect.center
        self.assertGreater(after[0], before[0])
        self.assertLess(after[1], before[1])
        self.assertGreater(len(self.game.bullets), 0)
        self.finger(pygame.FINGERUP)
        self.assertIsNone(self.game.touch_id)
        self.assertEqual(self.game.touch_delta, [0, 0])

    def test_second_finger_does_not_take_over(self):
        self.finger(pygame.FINGERDOWN)
        self.finger(pygame.FINGERDOWN, finger_id=2)
        self.finger(pygame.FINGERUP, finger_id=2)
        self.assertEqual(self.game.touch_id, 1)

    def test_letterbox_and_scaled_coordinates(self):
        self.game.native_width, self.game.native_height = 400, 800
        self.game._compute_display_rect()
        self.game._pointer_down(1, (200, 20))
        self.assertIsNone(self.game.touch_id)
        self.game._pointer_down(1, (200, 400))
        self.game._pointer_move(1, (220, 410))
        self.assertEqual(self.game.touch_delta, [40, 20])

    def test_focus_loss_pauses_and_clears_input(self):
        self.finger(pygame.FINGERDOWN)
        pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.game._handle_events()
        self.assertTrue(self.game.paused)
        self.assertIsNone(self.game.touch_id)
        before = self.game.player.rect.copy()
        self.game._update()
        self.assertEqual(before, self.game.player.rect)

    def test_touch_restart_and_pause_resume(self):
        self.game.game_over = True
        self.game._pointer_down(1, self.game.display_rect.center)
        self.assertFalse(self.game.game_over)
        self.assertEqual(self.game.lives, settings.STARTING_LIVES)
        self.game.paused = True
        self.game._pointer_down(1, self.game.display_rect.center)
        self.assertFalse(self.game.paused)
        self.assertIsNone(self.game.touch_id)

    def test_resize_clears_gesture_and_keeps_aspect(self):
        self.finger(pygame.FINGERDOWN)
        pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE, w=390, h=844))
        self.game._handle_events()
        self.assertIsNone(self.game.touch_id)
        self.assertLessEqual(self.game.display_rect.width, 390)
        self.assertLessEqual(self.game.display_rect.height, 844)
        self.assertAlmostEqual(
            self.game.display_rect.width / self.game.display_rect.height,
            800 / 600, places=2
        )
        self.game._draw()

    def test_player_stays_in_bounds(self):
        keys = pygame.key.get_pressed()
        self.game.player.update(keys, (10000, -10000))
        self.assertEqual(self.game.player.rect.right, settings.SCREEN_WIDTH)
        self.assertEqual(self.game.player.rect.top, 0)

    def test_browser_start_screen(self):
        with patch("game.sys.platform", "emscripten"):
            game = Game()
        self.assertTrue(game.paused)
        game._draw()
        game._pointer_down(1, game.display_rect.center)
        self.assertFalse(game.paused)

    def test_async_loop_exits(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        asyncio.run(self.game.run())


if __name__ == "__main__":
    unittest.main()
