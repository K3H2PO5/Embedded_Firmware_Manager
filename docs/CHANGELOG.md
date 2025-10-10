# 变更日志 / Changelog

所有重要的项目变更都将记录在此文件中。  
All notable changes to this project will be documented in this file.

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，  
Format based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。  
This project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/).

## [1.0.5.1] - 2025-10-10

### 修复 / Fixed
- **[重要]** 修复IAR编译命令缺少`-make`参数导致编译失败的问题 / Fixed IAR compilation failure due to missing `-make` parameter
- **[重要]** 修复IAR编译工作目录设置错误导致无法生成bin/out文件的问题 / Fixed incorrect working directory setting causing failure to generate bin/out files
- 修复IAR编译器初始化时日志输出路径混淆的问题 / Fixed path confusion in logger output during IAR builder initialization
- 修复`clean_project()`方法工作目录设置错误 / Fixed incorrect working directory setting in `clean_project()` method
- 修复权限检查和环境诊断中的路径引用错误 / Fixed path reference errors in permission checks and environment diagnostics

### 技术细节 / Technical Details
- 增量编译命令从 `IarBuild.exe project.ewp Debug` 修正为 `IarBuild.exe project.ewp -make Debug`
- 工作目录从项目根目录修正为.ewp文件所在目录
- 统一使用`self.iar_project_path`代替混淆的`self.project_path`

### 相关文档 / Related Documentation
- 新增 `docs/BUGFIX_IAR_COMPILE.md` 详细说明修复内容

## [1.0.5.0] - 2025-01-14

### 重大更新 / Major Updates
- 工具重命名为"嵌入式固件管理工具" / Renamed tool to "Embedded Firmware Manager"
- 新增MDK (Keil uVision)工具链支持 / Added MDK (Keil uVision) toolchain support
- 重构为模块化架构，采用工厂模式设计 / Refactored to modular architecture with factory pattern design

### 新增功能 / New Features
- 新增编译工具选择功能，支持IAR和MDK切换 / Added compilation tool selection feature supporting IAR and MDK switching
- 新增MDK项目文件解析功能，支持.uvprojx文件 / Added MDK project file parsing supporting .uvprojx files
- 新增MDK编译支持，使用UV4.exe命令行工具 / Added MDK compilation support using UV4.exe command-line tool
- 新增MDK二进制文件支持，支持.axf文件发布 / Added MDK binary file support for .axf file publishing
- 新增工具链路径独立配置，IAR和MDK路径分别存储 / Added independent toolchain path configuration with separate IAR and MDK path storage
- 新增专业图标设计，提升工具专业形象 / Added professional icon design to enhance tool's professional image

### 重构 / Refactored
- 重构项目结构，创建lib_IAR和lib_MDK模块库 / Refactored project structure creating lib_IAR and lib_MDK module libraries
- 重构日志系统，创建lib_logger统一日志模块 / Refactored logging system creating lib_logger unified logger module
- 重构文件管理器，分离IAR和MDK特定实现 / Refactored file managers separating IAR and MDK specific implementations
- 重构项目分析器，支持不同工具链的项目文件格式 / Refactored project analyzers supporting different toolchain project file formats
- 重构信息管理器，合并配置分析和信息文件更新功能 / Refactored info managers merging configuration analysis and info file update functionality
- 重构路径管理器，支持不同工具链的路径管理 / Refactored path managers supporting different toolchain path management
- 引入工厂模式，实现动态工具链选择 / Introduced factory pattern for dynamic toolchain selection

### 优化 / Improved
- 优化用户界面，动态显示当前选择的工具链路径 / Optimized user interface to dynamically display currently selected toolchain path
- 优化配置管理，支持工具链特定配置 / Optimized configuration management supporting toolchain-specific configurations
- 优化错误处理，提供更详细的工具链特定错误信息 / Optimized error handling providing more detailed toolchain-specific error messages
- 优化日志系统，统一所有模块的日志输出 / Optimized logging system unifying log output from all modules
- 优化文件名生成，支持分支名称参数 / Optimized filename generation supporting branch name parameters
- 优化远程发布，使用项目名称_分支名称格式创建子目录 / Optimized remote publishing using project_name_branch_name format for subdirectories

### 修复 / Fixed
- 修复时间戳功能，确保文件名时间戳正确添加 / Fixed timestamp functionality ensuring filename timestamps are correctly added
- 修复Git分支检测，增强分支名称获取的可靠性 / Fixed Git branch detection enhancing reliability of branch name retrieval
- 修复配置加载优先级，确保用户配置正确加载 / Fixed configuration loading priority ensuring user configuration is correctly loaded
- 修复日志路径问题，优化exe环境下的日志文件管理 / Fixed log path issues optimizing log file management in exe environment

## [1.0.4.2] - 2025-01-13

### 重构 / Refactored
- 统一工具版本号管理，将版本号集中存储到version.py文件中 / Unified tool version management by centralizing version numbers in version.py file
- 简化tool_version_manager.py，移除复杂的异常处理和默认值逻辑 / Simplified tool_version_manager.py by removing complex exception handling and default value logic
- 优化版本号更新机制，直接修改version.py文件而不是main.py / Optimized version update mechanism by directly modifying version.py instead of main.py
- 删除main.py中的版本号定义，统一从version.py导入 / Removed version number definition from main.py, unified import from version.py
- 增强版本号匹配模式，支持数量不定的空格和注释 / Enhanced version number matching pattern to support variable spaces and comments
- 合并increment_tool_version.py到tool_version_manager.py，消除功能重复 / Merged increment_tool_version.py into tool_version_manager.py to eliminate functional duplication
- 简化构建流程，统一版本管理接口 / Simplified build process with unified version management interface
- 新增高级版本递增功能，支持进位和格式化 / Added advanced version increment functionality with carry-over and formatting support
- 更新build_exe.py，直接使用ToolVersionManager进行版本管理 / Updated build_exe.py to directly use ToolVersionManager for version management

### 修复 / Fixed
- 修复语言切换后某些控件仍显示中文的问题，完善界面本地化 / Fixed issue where some controls still displayed Chinese after language switch, improved interface localization
- 修复语言切换后勾选框文本不更新的问题，确保界面完全本地化 / Fixed issue where checkbox text didn't update after language switch, ensuring complete interface localization
- 修复设置窗口中硬编码的中文标签，实现完全本地化 / Fixed hardcoded Chinese labels in settings window, achieving complete localization
- 修复主界面编译配置相关硬编码中文，添加完整翻译支持 / Fixed hardcoded Chinese text for build configuration in main interface, added complete translation support
- 修复进度条状态文本的硬编码中文，实现状态消息本地化 / Fixed hardcoded Chinese text for progress bar status, implemented status message localization

### 优化 / Improved
- 优化语言下拉框显示格式，显示友好的语言文本而不是语言代码 / Optimized language dropdown display format to show friendly language text instead of language codes
- 优化语言切换时的窗口尺寸调整，确保英文界面使用合适的宽度 / Optimized window size adjustment during language switch, ensuring English interface uses appropriate width
- 优化设置页面宽度，中文界面600px，英文界面670px / Optimized settings page width: 600px for Chinese interface, 670px for English interface
- 优化语言切换机制，实现立即生效无需保存配置 / Optimized language switching mechanism for immediate effect without requiring configuration save
- 优化界面布局，语言下拉框宽度调整为15个字符 / Optimized interface layout with language dropdown width adjusted to 15 characters

### 新增功能 / New Features
- 新增完整的三种语言支持（简体中文、繁体中文、英文） / Added complete three-language support (Simplified Chinese, Traditional Chinese, English)
- 新增语言切换时的实时窗口尺寸调整功能 / Added real-time window size adjustment functionality during language switching
- 新增所有界面元素的本地化翻译，包括状态消息、日志信息等 / Added localization translations for all interface elements including status messages and log information
- 新增语言选项的友好显示格式，提升用户体验 / Added friendly display format for language options to improve user experience

## [1.0.4.1] - 2025-01-13

### 修复 / Fixed
- 修复主界面IAR路径显示"未配置"的问题 / Fixed issue where IAR path displayed as "未配置" on main interface
- 修复_load_user_config_to_ui方法中的变量作用域问题，确保project_path变量正确初始化 / Fixed variable scope issue in _load_user_config_to_ui method, ensure project_path variable is properly initialized
- 修复项目切换时用户配置信息丢失的问题 / Fixed issue where user configuration was lost when switching projects
- 简化save_config方法，只更新项目路径，保留用户的其他配置设置 / Simplified save_config method to only update project path while preserving other user settings
- 优化配置保存逻辑，避免使用默认值覆盖用户设置 / Optimized configuration saving logic to avoid overwriting user settings with default values

### 优化 / Improved
- 优化CRC32计算算法，使用IEEE 802.3标准多项式，提高校验准确性 / Optimized CRC32 calculation algorithm using IEEE 802.3 standard polynomial for improved checksum accuracy
- 改进文件CRC计算逻辑，支持分段计算并排除CRC值和hash值存储区域 / Improved file CRC calculation logic with segmented calculation excluding CRC and hash value storage regions
- 优化二进制文件修改性能，减少内存占用和计算时间 / Optimized binary file modification performance, reduced memory usage and calculation time
- 增强CRC计算错误处理，提供更详细的调试信息 / Enhanced CRC calculation error handling with more detailed debug information
- 优化IAR项目文件(.ewp)解析功能，支持多配置项目自动识别 / Optimized IAR project file (.ewp) parsing functionality with automatic multi-configuration detection
- 改进ICF文件解析算法，支持多种内存布局格式和$PROJ_DIR$宏解析 / Improved ICF file parsing algorithm supporting multiple memory layout formats and $PROJ_DIR$ macro resolution
- 增强ewp文件XML解析性能，使用lxml库提升解析速度 / Enhanced ewp file XML parsing performance using lxml library for faster parsing
- 优化编译输出文件查找逻辑，自动识别bin和out文件路径 / Optimized build output file discovery logic with automatic bin and out file path identification

### 新增功能 / New Features
- 增强ewp文件多配置支持，自动识别项目中的所有编译配置 / Enhanced ewp file multi-configuration support with automatic detection of all build configurations
- 添加配置选择下拉框，支持用户选择不同的编译配置 / Added configuration selection dropdown supporting user selection of different build configurations
- 实现一键执行功能，自动完成Git检查、版本检查、编译、文件处理等全流程 / Implemented one-click execution feature automatically completing Git check, version check, compilation, and file processing workflow
- 优化配置切换体验，选择配置后自动更新相关路径和设置 / Optimized configuration switching experience with automatic path and settings update upon configuration selection
- 添加配置刷新功能，支持动态检测项目配置变化 / Added configuration refresh functionality supporting dynamic detection of project configuration changes


## [1.0.3.8] - 2025-01-09

### 修复 / Fixed
- 修复ICF文件解析问题，正确解析IlinkIcfFile节点中的$PROJ_DIR$宏 / Fixed ICF file parsing issue, correctly parse $PROJ_DIR$ macro in IlinkIcfFile node
- 移除path_manager.py中硬编码的默认文件名，要求必须传入参数避免个人习惯影响 / Removed hardcoded default file names in path_manager.py, require parameters to avoid personal habits affecting others
- 修复配置文件优先级问题，确保用户界面指定的项目路径优先于user_config.json中的设置 / Fixed configuration priority issue, ensure UI-specified project path takes precedence over user_config.json settings
- 确保所有配置文件路径都使用相对路径，与主程序文件在同一目录 / Ensure all configuration file paths use relative paths, same directory as main program file
- 移除os.getcwd()的使用，避免打包exe时的工作目录问题 / Removed os.getcwd() usage to avoid working directory issues when packaging exe
- 移除ICF文件默认路径搜索逻辑，如果ewp文件中没有ICF文件引用则直接报错 / Removed ICF file default path search logic, directly report error if no ICF file reference found in .ewp file

### 改进 / Improved
- 优化代码结构，移除重复的配置文件 / Optimized code structure, removed duplicate configuration files
- 改进错误处理，项目路径无效时直接报错而不是使用当前工作目录 / Improved error handling, directly report error when project path is invalid instead of using current working directory

### 清理 / Cleanup
- 删除重复的config.example.json文件，保留config.json作为实际配置文件 / Removed duplicate config.example.json files, kept config.json as actual configuration file
- 修复build_exe.py中对已删除文件的引用，避免打包时出现文件找不到错误 / Fixed references to deleted files in build_exe.py to avoid file not found errors during packaging

## [1.0.3.7] - 2025-01-09

### 修复 / Fixed
- 修复IAR编译命令路径错误，使用正确的ewp文件路径而不是项目根目录 / Fixed IAR compilation command path error, use correct .ewp file path instead of project root directory
- 修复bin文件查找逻辑，严格匹配ewp文件名对应的bin文件，避免选择错误的备份文件 / Fixed bin file finding logic, strictly match .ewp filename corresponding bin file, avoid selecting wrong backup files
- 修复exe运行时配置文件路径问题，使用绝对路径确保配置文件正确加载 / Fixed exe runtime configuration file path issue, use absolute paths to ensure configuration files are loaded correctly
- 修复项目路径和ewp文件路径混淆问题，确保路径变量正确分离 / Fixed project path and .ewp file path confusion issue, ensure path variables are correctly separated
- 修复配置文件选择对话框文件类型筛选，添加对C++文件(.cpp, .cc, .cxx, .hpp, .hxx)的支持 / Fixed configuration file selection dialog file type filter, added support for C++ files (.cpp, .cc, .cxx, .hpp, .hxx)

### 改进 / Improved
- 改进编译命令构建逻辑，确保IAR编译器能正确识别项目文件 / Improved compilation command building logic, ensure IAR compiler can correctly identify project files
- 改进bin文件查找策略，移除"查找最新文件"逻辑，采用严格文件名匹配 / Improved bin file finding strategy, removed "find latest file" logic, adopted strict filename matching
- 改进错误处理，提供更详细的路径和文件存在性检查日志 / Improved error handling, provide more detailed path and file existence check logs
- 改进配置管理，确保exe和源码版本都能正确加载配置文件 / Improved configuration management, ensure both exe and source code versions can correctly load configuration files
- 优化配置结构，将版本变量名配置移至用户配置，统一使用firmware_version_keyword / Optimized configuration structure, moved version variable name configuration to user config, unified use of firmware_version_keyword
- 改进版本号匹配正则表达式，支持不同数量的空格和注释（单行注释//、多行注释/* */） / Improved version number matching regex, support different amounts of spaces and comments (single-line //, multi-line /* */)
- 修复路径管理中的硬编码问题，新增通用的find_info_file方法支持多种文件名和扩展名 / Fixed hardcoded paths in path management, added generic find_info_file method supporting multiple file names and extensions
- 优化方法命名，明确区分工具路径和项目路径，避免混淆 / Optimized method naming, clearly distinguish between tool paths and project paths to avoid confusion
- 修复PathManager初始化问题，移除os.getcwd()避免打包exe时的工作目录问题 / Fixed PathManager initialization issue, removed os.getcwd() to avoid working directory problems when packaging exe
- 优化代码结构，移除main.py中重复的_find_info_file方法，统一使用PathManager的find_info_file方法 / Optimized code structure, removed duplicate _find_info_file method in main.py, unified use of PathManager's find_info_file method
- 合并重复的文件查找方法，删除config_analyzer.py中的find_config_file方法，统一使用path_manager.find_info_file / Merged duplicate file search methods, removed find_config_file from config_analyzer.py, unified use of path_manager.find_info_file
- 优化文件搜索性能，在find_info_file方法中排除.git、.clion、.idea和cmake开头的目录，避免搜索构建系统生成的临时文件 / Optimized file search performance, excluded .git, .clion, .idea and cmake* directories in find_info_file method to avoid searching build system generated temporary files
- 改进错误信息显示，区分"未找到文件"和"找到多个文件"的情况，在找到多个文件时列出所有文件路径，提供更明确的错误提示 / Improved error message display, distinguish between "file not found" and "multiple files found" cases, list all file paths when multiple files are found, provide clearer error prompts
- 修复错误信息前后矛盾的问题，统一使用find_info_file_with_details方法，避免重复搜索和矛盾的错误提示 / Fixed contradictory error messages, unified use of find_info_file_with_details method to avoid duplicate searches and conflicting error prompts
- 优化弹窗错误信息显示，建议用户查看日志输出获取详细信息，避免弹窗信息过于冗长 / Optimized popup error message display, suggest users check log output for detailed information, avoid overly verbose popup messages

### 移除 / Removed
- 移除备份spec文件功能，简化PyInstaller构建过程 / Removed backup spec file functionality, simplified PyInstaller build process
- 移除_find_latest_bin_file方法，采用更可靠的严格匹配策略 / Removed _find_latest_bin_file method, adopted more reliable strict matching strategy

## [1.0.3.6] - 2025-01-XX

### 新增 / Added
- 添加.out文件发布功能，支持同时发布.bin和.out文件到本地和远程目录 / Added .out file publishing feature, support publishing both .bin and .out files to local and remote directories
- 优化设置页面布局，调整复选框间距和对齐方式 / Optimized settings page layout, adjusted checkbox spacing and alignment

### 改进 / Improved
- 改进文件发布逻辑，确保.out文件与.bin文件使用相同的命名规则 / Improved file publishing logic, ensure .out files use the same naming convention as .bin files
- 优化远程发布功能，支持.out文件的远程发布 / Optimized remote publishing feature, support .out file remote publishing
- 改进设置页面用户体验，相关复选框布局更加美观 / Improved settings page user experience, related checkboxes layout more aesthetically pleasing

### 修复 / Fixed
- 修复.out文件查找逻辑，确保能正确找到对应的.out文件 / Fixed .out file finding logic, ensure correct .out file can be found
- 修复设置页面复选框对齐问题 / Fixed settings page checkbox alignment issues

## [1.0.3.5] - 2025-01-XX

### 新增 / Added
- 添加文件名时间戳控制选项，用户可选择是否在文件名中添加时间戳 / Added filename timestamp control option, users can choose whether to add timestamp to filename
- 优化设置页面布局，将相关复选框放在同一行以节省空间 / Optimized settings page layout, place related checkboxes on the same row to save space

### 改进 / Improved
- 改进文件发布逻辑，支持可选的文件名时间戳功能 / Improved file publishing logic, support optional filename timestamp feature
- 改进设置页面用户体验，相关功能选项布局更加紧凑 / Improved settings page user experience, related function options layout more compact

### 修复 / Fixed
- 修复配置合并逻辑，确保新配置项能正确添加到现有用户配置中 / Fixed configuration merge logic, ensure new configuration items can be correctly added to existing user configurations

## [1.0.3.4] - 2025-01-XX

### 新增 / Added
- 添加哈希校验和功能，支持__hash_value变量 / Added hash checksum functionality, support for __hash_value variable
- 添加Flash起始地址显示，在主界面显示当前配置的Flash起始地址 / Added Flash start address display on main interface
- 添加环境诊断功能，帮助排查打包exe运行问题 / Added environment diagnosis feature to help troubleshoot packaged exe issues
- 添加详细的路径搜索和验证日志 / Added detailed path search and validation logging

### 改进 / Improved
- 优化主界面布局，调整信息显示顺序：IAR路径、Flash起始地址、Git状态、固件版本 / Optimized main interface layout, adjusted information display order: IAR path, Flash start address, Git status, firmware version
- 改进IAR路径查找逻辑，确保始终返回有效的exe文件路径 / Improved IAR path finding logic, ensure always returns valid exe file path
- 优化subprocess调用策略，支持多种调用方式以提高兼容性 / Optimized subprocess calling strategy, support multiple calling methods for better compatibility
- 改进错误处理，提供更详细的错误信息和诊断日志 / Improved error handling, provide more detailed error messages and diagnostic logs

### 修复 / Fixed
- 修复打包exe时出现的[WinError 5] 拒绝访问权限错误 / Fixed [WinError 5] Access Denied error when running packaged exe
- 修复IAR路径解析问题，避免返回目录路径而不是exe文件路径 / Fixed IAR path parsing issue, avoid returning directory path instead of exe file path
- 修复subprocess调用时路径包含空格的问题 / Fixed subprocess calling issue with paths containing spaces
- 修复hash_value_offset未设置的问题，支持uint8_t数组类型 / Fixed hash_value_offset not set issue, support uint8_t array type

## [1.0.2.1] - 2024-01-XX

### 新增 / Added
- 添加Git提交对话框，支持自定义提交信息 / Added Git commit dialog with custom commit message support
- 添加Release Notes自动生成功能 / Added automatic Release Notes generation
- 添加远程发布功能，支持将固件发布到远程目录 / Added remote publishing feature, support publishing firmware to remote directories
- 添加工具版本管理，支持打包时自动递增版本号 / Added tool version management, support automatic version increment during packaging
- 添加多显示器支持，对话框自动居中到主窗口 / Added multi-monitor support, dialogs automatically center to main window
- 添加Enter键换行，Ctrl+Enter确认的提交对话框交互 / Added Enter for new line, Ctrl+Enter to confirm commit dialog interaction

### 改进 / Improved
- 优化Git集成，合并代码更改和版本更新为单个提交 / Optimized Git integration, merge code changes and version updates into single commit
- 改进路径管理，避免打包exe后的路径问题 / Improved path management, avoid path issues after packaging exe
- 优化用户界面，重命名"固件发布目录"为"本地发布目录" / Optimized user interface, renamed "Firmware Publish Directory" to "Local Publish Directory"
- 改进版本号递增逻辑，确保每个版本部分为单数字 / Improved version increment logic, ensure each version part is single digit

### 修复 / Fixed
- 修复配置保存问题，确保用户设置正确写入配置文件 / Fixed configuration save issue, ensure user settings are correctly written to config files
- 修复远程发布文件复制问题 / Fixed remote publishing file copying issues
- 修复对话框在多显示器环境下的显示问题 / Fixed dialog display issues in multi-monitor environments
- 修复工具版本号显示和递增逻辑 / Fixed tool version number display and increment logic

### 移除 / Removed
- 移除.out文件夹相关功能，简化工具结构 / Removed .out folder related functionality, simplified tool structure
- 移除build.bat文件，使用Python脚本进行打包 / Removed build.bat file, use Python script for packaging