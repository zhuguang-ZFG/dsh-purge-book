"""Three authored plates for the fixed-commit migration case."""
from sketchbook import Sketch, INK, PAPER, ACCENT, MUTED, PALE, RUST, FAINT, HAND, MONO


def migration():
    s = Sketch('migration', '改名沿四处传播', '命令、路由、状态目录与运行时标记分别改名；版本仍为 2.0.0，目标仍是 DSH。')
    s.heading('6·2', '改名沿四处传播', '版本号没有替你区分这两个包。')
    s.text(345, 218, 'dsh-purge-safe', 30, INK, MONO, 'middle')
    s.text(920, 218, 'pi-purge', 30, ACCENT, MONO, 'middle')
    rows = [('命令', 'bin/dsh-purge-safe.js', 'bin/pi-purge.js'),
            ('路由', '/dsh-purge-safe/*', '/pi-purge/*'),
            ('状态', 'home/dsh-purge-safe/', 'home/pi-purge/'),
            ('标记', 'dshpg-* / dshPurge', 'pipg-* / piPurge')]
    for i, (label, before, after) in enumerate(rows):
        y = 260 + i * 68
        s.text(65, y+35, label, 24, MUTED, HAND)
        s.box(165, y, 375, 51, fill=PAPER, weight=1.8)
        s.box(735, y, 385, 51, fill=PALE, weight=1.8, color=ACCENT)
        s.text(185, y+33, before, 22, INK, MONO)
        s.text(755, y+33, after, 22, ACCENT, MONO)
        s.arrow(566, y+26, 708, y+26, color=MUTED, weight=1.8)
    s.text(600, 578, '同为 2.0.0  /  仍是 DSH  /  59 条补丁定义', 25, INK, HAND, 'middle')
    s.footer('身份以仓库、固定提交和实际路径共同识别。', 'MIGRATION')
    return s


def shared():
    s = Sketch('shared', '分开的记录，共同的落点', '独立状态目录与备份后缀分列两侧，共享规则、事实库、预设与宿主放在中间。')
    s.heading('6·3', '分开的记录，共同的落点', '下列路径按相同 DSH_HOME 和默认数据配置示意。')
    for x, title, directory, suffix, color in [
        (65, '旧包记录', 'dsh-purge-safe/', '.dshpurge.bak', INK),
        (800, '新包记录', 'pi-purge/', '.pipurge.bak', ACCENT)]:
        s.path(f'M{x} 258 L{x+75} 258 L{x+94} 278 L{x+330} 278 L{x+330} 482 L{x} 482 Z',
               fill=PALE if x==65 else RUST, color=color, weight=2.5)
        s.text(x+165, 233, title, 27, color, HAND, 'middle')
        s.text(x+18, 326, directory, 24, color, MONO)
        s.text(x+18, 376, '状态 / host-backups', 22, color, HAND)
        s.text(x+18, 429, suffix, 24, color, MONO)
    s.box(443, 247, 304, 272, fill=PAPER, weight=2.3)
    s.text(595, 287, '默认共同路径', 26, INK, HAND, 'middle')
    for i, line in enumerate(['rules/', 'redteam/', 'redteam/skills/', '.agent-presets/redteam/']):
        s.text(595, 335+i*44, line, 20, MUTED, MONO, 'middle')
    s.arrow(405, 370, 435, 370, color=MUTED, weight=1.8)
    s.arrow(790, 370, 755, 370, color=MUTED, weight=1.8)
    s.text(600, 569, '宿主文件也可能相同；切换前先恢复旧包并核对。', 25, ACCENT, HAND, 'middle')
    s.footer('不同备份后缀，不等于不同宿主。', 'SHARED PATHS')
    return s


def guard():
    s = Sketch('guard', '同包去重，两包仍各改一次', '上排同包重复安装只更新 slot；下排旧包与新包各自包装，假对象执行两个 rewrite。')
    s.heading('3·2', '同包去重，两包仍各改一次', '离线假对象实验：观察调用次数，不发送模型请求。')
    s.text(70, 244, '同包两次', 27, INK, HAND)
    for x, text in [(290, '安装旧包'), (570, '再装旧包'), (920, '一个 slot')]:
        s.box(x-25, 209, 245, 72, fill=PALE, weight=2)
        s.text(x+97, 254, text, 26, INK, HAND, 'middle')
    s.arrow(524, 247, 537, 247, weight=1.8)
    s.arrow(809, 247, 888, 247, weight=1.8)
    s.rule(66, 326, 1060)
    s.text(70, 401, '两包各装', 27, ACCENT, HAND)
    for x, text, tint in [(290, '旧包 slot', PALE), (570, '新包 slot', RUST), (920, '两次 rewrite', PAPER)]:
        s.box(x-25, 363, 245, 72, fill=tint, color=ACCENT, weight=2)
        s.text(x+97, 408, text, 26, ACCENT, HAND, 'middle')
    s.arrow(524, 400, 537, 400, color=ACCENT, weight=1.8)
    s.arrow(809, 400, 888, 400, color=ACCENT, weight=1.8)
    s.text(600, 501, 'dsh-purge-safe.assembleGuard', 25, INK, MONO, 'middle')
    s.text(600, 547, 'pi-purge.assembleGuard', 25, ACCENT, MONO, 'middle')
    s.footer('只证明假对象上的两次改写；真实宿主与最终正文另验。', 'TWO NAMESPACES')
    return s
