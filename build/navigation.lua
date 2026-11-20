-- Shared anchors for the EPUB reader index and PDF outline destinations.
local function text(s) return pandoc.utils.stringify(s) end

function Pandoc(doc)
  local file = assert(io.open('illustrations/manifest.json', 'r'))
  local plates = pandoc.json.decode(file:read('*a'))
  file:close()
  local notes_file = assert(io.open('build/figure-notes.json', 'r'))
  local figure_notes = pandoc.json.decode(notes_file:read('*a'))
  notes_file:close()
  local epub = FORMAT:match('epub') ~= nil
  local titles = {}
  for _, plate in ipairs(plates) do titles[plate.key] = plate.title end
  local entries, figures, headings = {}, {}, {}
  local owner, chapter = nil, '卷首'
  local first_chapter
  for index, block in ipairs(doc.blocks) do
    if block.t == 'Header' then
      local title = text(block.content)
      if block.level == 1 then
        first_chapter = first_chapter or index
        chapter = title:match('第 %d 章') or (title:match('结语') and '结语') or title
      end
      owner = block.identifier
      local entry = {kind='heading', id=owner, title=title, level=block.level}
      table.insert(entries, entry)
      table.insert(headings, entry)
    elseif block.t == 'Figure' then
      local src
      block:walk {Image=function(img) src = src or img.src end}
      assert(src, 'Figure has no image')
      local key = src:match('([^/]+)%.svg$')
      assert(key, 'Figure must have an SVG source: ' .. src)
      local ch, num = key:match('^(%d%d).+%-(%d+)$')
      local id = 'fig-' .. (ch and (ch .. '-' .. num) or key)
      local note = assert(figure_notes[ch and (ch .. '-' .. num) or key], 'Missing figure reading notes: ' .. key)
      -- EPUB resolves cross-chapter links to Div anchors when splitting files.
      -- Keep the anchor outside Figure so its target is relocated with the chapter.
      block.identifier = ''
      local contents = {block}
      if epub then
        local lines = {'**读图说明**'}
        for _, sentence in ipairs(note.notes) do table.insert(lines, '- ' .. sentence) end
        table.insert(lines, '\n[查看原图](' .. src .. '){.figure-original}')
        table.insert(contents, pandoc.Div(pandoc.read(table.concat(lines, '\n\n')).blocks,
                                        pandoc.Attr('', {'figure-reading'})))
      end
      doc.blocks[index] = pandoc.Div(contents, pandoc.Attr(id, {'book-figure'}))
      local caption = text(block.caption.long)
      local entry = {kind='figure', id=id, title=titles[key] or caption, short=note.short, caption=caption,
                     owner=owner or '', chapter=chapter, source=src}
      table.insert(entries, entry)
      table.insert(figures, entry)
    end
  end
  assert(first_chapter, 'No chapter found')
  local specs = {
    {'1.5 ', '安装与首次验收'}, {'2.5 ', '备份与恢复'},
    {'3.2 ', '提示词组装'}, {'4.2 ', '四项验收'},
    {'5.4 ', '处理任务回报'}, {'6.2 ', '维护检查表'},
    {'A.1 ', '命令速查'}, {'B.1 ', '术语索引'},
  }
  local shortcuts = {}
  for _, spec in ipairs(specs) do
    local found
    for _, entry in ipairs(headings) do
      if entry.title:sub(1, #spec[1]) == spec[1] then
        found = {id=entry.id, title=spec[2]}
        table.insert(shortcuts, found)
        break
      end
    end
    assert(found, 'Missing shortcut heading: ' .. spec[1])
  end
  local md = {'## 翻阅索引 {#reader-index}', '',
              '按问题查找时，可从下面的书签进入；插图链接直接跳到图页。', '',
              '**常用书签**', '', '| 操作与排查 | 维护与速查 |', '| --- | --- |'}
  local function link(item) return '[' .. (item.short or item.title) .. '](#' .. item.id .. ')' end
  for i=1, 4 do table.insert(md, '| ' .. link(shortcuts[i]) .. ' | ' .. link(shortcuts[i+4]) .. ' |') end
  table.insert(md, '\n**插图索引**\n')
  local groups, order = {}, {}
  for _, figure in ipairs(figures) do
    if not groups[figure.chapter] then
      groups[figure.chapter] = {}
      table.insert(order, figure.chapter)
    end
    table.insert(groups[figure.chapter], link(figure))
  end
  for _, name in ipairs(order) do
    table.insert(md, '- ' .. name .. '：' .. table.concat(groups[name], '；'))
  end
  local index_blocks = pandoc.read(table.concat(md, '\n')).blocks
  for i, entry in ipairs(entries) do
    if entry.kind == 'heading' and entry.level == 1 then
      table.insert(entries, i, {kind='heading', id='reader-index', title='翻阅索引', level=2})
      break
    end
  end
  for i=#index_blocks, 1, -1 do doc.blocks:insert(first_chapter, index_blocks[i]) end
  doc = doc:walk {Table=function(tbl)
    local labels = {}
    if tbl.head and #tbl.head.rows > 0 then
      for i, cell in ipairs(tbl.head.rows[1].cells) do labels[i] = text(cell.contents) end
    end
    local rows, chars = 0, 0
    for _, body in ipairs(tbl.bodies) do
      for _, row in ipairs(body.body) do
        rows = rows + 1
        for i, cell in ipairs(row.cells) do
          chars = chars + utf8.len(text(cell.contents))
          if epub and labels[i] then
            local label = pandoc.Span({pandoc.Str(labels[i])}, pandoc.Attr('', {'cell-label'}))
            if cell.contents[1] and (cell.contents[1].t == 'Plain' or cell.contents[1].t == 'Para') then
              cell.contents[1].content:insert(1, label)
            else cell.contents:insert(1, pandoc.Plain({label})) end
          end
        end
      end
    end
    if not epub and rows <= 8 and chars < 620 then
      return pandoc.Div({tbl}, pandoc.Attr('', {'compact-table'}))
    end
    return tbl
  end}
  local output = assert(io.open('build/tmp/navigation.json', 'w'))
  output:write(pandoc.json.encode({entries=entries, shortcuts=shortcuts}))
  output:close()
  return doc
end
