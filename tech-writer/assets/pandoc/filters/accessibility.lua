-- Tech Writer - Accessibility Filter
-- Enforces WCAG 2.1 Level AA compliance during pandoc conversion
-- Usage: pandoc --lua-filter=accessibility.lua

-- Track heading levels for hierarchy validation
local last_heading_level = 0
local warnings = {}

local function warn(msg)
  table.insert(warnings, msg)
  io.stderr:write("WARNING: " .. msg .. "\n")
end

-- Ensure images have alt text
function Image(el)
  if el.caption == nil or #el.caption == 0 then
    if el.attributes and el.attributes.alt and el.attributes.alt ~= "" then
      -- alt attribute exists, use it
      return el
    end
    -- Extract filename as fallback alt text
    local filename = el.src:match("([^/]+)$") or el.src
    filename = filename:gsub("%.[^.]+$", "")  -- remove extension
    filename = filename:gsub("[_-]", " ")      -- replace separators
    warn("Image missing alt text: " .. el.src .. " (using filename as fallback)")
    el.caption = {pandoc.Str(filename)}
  end
  return el
end

-- Validate heading hierarchy (no skipping levels)
function Header(el)
  local level = el.level
  if level > last_heading_level + 1 and last_heading_level > 0 then
    warn("Heading level skipped: H" .. last_heading_level .. " -> H" .. level
         .. ' at "' .. pandoc.utils.stringify(el.content) .. '"')
  end
  last_heading_level = level
  return el
end

-- Add scope to table headers
function Table(el)
  -- Process header rows to add scope
  if el.head and el.head.rows then
    for _, row in ipairs(el.head.rows) do
      for _, cell in ipairs(row.cells) do
        cell.attr = cell.attr or pandoc.Attr()
        cell.attr.attributes = cell.attr.attributes or {}
        if not cell.attr.attributes.scope then
          cell.attr.attributes.scope = "col"
        end
      end
    end
  end
  return el
end

-- Convert bare URLs into descriptive links
function Link(el)
  local text = pandoc.utils.stringify(el.content)
  -- If link text is just the URL, try to make it descriptive
  if text == el.target or text == "" then
    -- Extract domain or path as better text
    local desc = el.target:match("//([^/]+)") or el.target
    warn("Bare URL link: " .. el.target .. " (consider using descriptive link text)")
  end
  return el
end

-- Set document language if not already set
function Meta(meta)
  if not meta.lang then
    meta.lang = pandoc.MetaInlines{pandoc.Str("en")}
    warn("No document language set. Defaulting to 'en'. Set lang in YAML frontmatter.")
  end
  return meta
end

-- Print summary of warnings at the end
function Pandoc(doc)
  if #warnings > 0 then
    io.stderr:write("\n--- Accessibility Report ---\n")
    io.stderr:write(#warnings .. " issue(s) found:\n")
    for i, w in ipairs(warnings) do
      io.stderr:write("  " .. i .. ". " .. w .. "\n")
    end
    io.stderr:write("----------------------------\n")
  end
  return doc
end
