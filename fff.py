# 時間がなかった時よう
def update(self):
        # ファイヤーボールを移動
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # 敵に当たったら消去
        hit = pygame.sprite.spritecollide(self, teki_hako, True)
        if hit:
            self.kill()
