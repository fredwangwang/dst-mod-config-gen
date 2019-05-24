# dst-mod-config-gen
Generate modoverrides.lua for dedicated don't starve together server.


## How to use:
1. Make sure you have Python 3 installed
1. Download `modoverridesGen.py` script from [here](https://raw.githubusercontent.com/fredwangwang/dst-mod-config-gen/master/modoverridesGen.py)
1. Drop the script into `mods` folder
1. Execute `modoverridesGen.py` by double clicking on it, or run `python modoverridesGen.py` from commandline
1. Your `modoverrides.lua` will be ready in the same folder!

## Feature:
* Generate `modoverrides.lua` for you
* Auto drops staled config options when the mod get updated
* Shows avaiable configuration options with each configuration options entry
* Preserve config changes you made in the `modoverrides.lua` when running the script again

## Motivation:
This project is inspired by [DSTConfig](https://github.com/INpureProjects/DSTConfig). DSTConfig does a good job in
generating the `modoverrides.lua`, and I've used it quite a bit when hosting my own dedicated server. However, it only generates
a skeleton `modoverrides.lua` with the default options chosed but not how to configure the options. Here is an example:
```lua
return {
  --Growable Marble Trees
  ["workshop-363989569"] = {enabled = true,
    configuration_options = {},
  },
  --Health Info
  ["workshop-375859599"] = {enabled = true,
    configuration_options = {
      ["show_type"] = 0,
      ["divider"] = 5,
      ["use_blacklist"] = true,
      ["unknwon_prefabs"] = 1,
      ["send_unknwon_prefabs"] = true,
      ["random_health_value"] = 0,
      ["random_range"] = 0,
   },
  },
}
```

I found myself need to go back and forth between `modinfo.lua` files and `modoverrides.lua` to figure out how to configure a mod,
which in my opinion defeats thepurpose of making the process of creating `modoverrides.lua` easier.
So I created this generator which imporves that.
As a comparasion, here is the sample `modoverrides.lua` file generated given the same mod as above:
```lua
return {
    -- Growable Marble Trees
    ["workshop-363989569"] = { enabled = true,
    },
    -- Health Info
    ["workshop-375859599"] = { enabled = true,
        configuration_options = {
        -- Show Type
        -- description = Value, data = 0
        -- description = Percentage, data = 1
        -- description = Both, data = 2
        ["show_type"] = 0,
        -- Divier Type
        -- description = 100/100, data = 0
        -- description = -100/100-, data = 1
        -- description = [100/100], data = 2
        -- description = (100/100), data = 3
        -- description = {100/100}, data = 4
        -- description = <100/100>, data = 5
        ["divider"] = 5,
        -- Use Black List
        -- description = Yes, data = true
        -- description = No, data = false
        ["use_blacklist"] = true,
        -- Unknown Objects
        -- description = Ignore, data = 0
        -- description = Players, data = 1
        -- description = Creatures, data = 2
        -- description = All, data = 3
        ["unknwon_prefabs"] = 1,
        -- Chance Fluctuation
        -- description = 0%, data = 0
        -- description = 5%, data = 0.05
        -- description = 10%, data = 0.1
        -- description = 15%, data = 0.15
        -- description = 25%, data = 0.25
        -- description = 30%, data = 0.3
        -- description = 40%, data = 0.4
        -- description = 50%, data = 0.5
        ["random_health_value"] = 0,
        -- Randomize Interval
        -- description = Always, data = 0
        -- description = 1%-99%, data = 0.01
        -- description = 5%-95%, data = 0.05
        -- description = 10%-90%, data = 0.1
        -- description = 15%-85%, data = 0.15
        ["random_range"] = 0,
        },
    },
}
```





