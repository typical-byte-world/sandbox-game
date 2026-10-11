"""Collision resolution in the original gameplay order."""


def handle_player_bullet_collisions(env):
    for bullet in env.bullets[:]:
        if env._handle_boss_bullet_collision(bullet):
            continue
        env._handle_enemy_bullet_collision(bullet)


def handle_boss_bullet_collision(env, bullet):
    if not env.boss:
        return False
    if not bullet.rect.colliderect(env.boss.rect):
        return False
    env.bullets.remove(bullet)
    env.boss.take_damage(1)
    env.stats.shots_hit += 1
    env.stats.score += 25
    if not env.boss.is_alive:
        env.stats.kills += 1
        env.stats.score += 1000
        env.boss = None
        env.stats.game_complete = True
    return True


def handle_enemy_bullet_collision(env, bullet):
    for enemy in env.enemies[:]:
        if not bullet.rect.colliderect(enemy.rect):
            continue
        env.bullets.remove(bullet)
        env.enemies.remove(enemy)
        env.stats.kills += 1
        env.stats.shots_hit += 1
        env.stats.score += 100
        return True
    return False


def resolve_enemy_projectiles(env):
    for bullet in env.enemy_bullets[:]:
        if not bullet.rect.colliderect(env.player.rect):
            continue
        env.enemy_bullets.remove(bullet)
        env.stats.lives -= 1
        if env.stats.lives <= 0:
            env.game_over = True
        break
