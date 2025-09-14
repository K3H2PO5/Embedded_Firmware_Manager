# 用户指南 / User Guide

## 目录 / Table of Contents

1. [快速开始 / Quick Start](#快速开始--quick-start)
2. [详细配置 / Detailed Configuration](#详细配置--detailed-configuration)
3. [功能详解 / Feature Details](#功能详解--feature-details)
4. [高级功能 / Advanced Features](#高级功能--advanced-features)
5. [故障排除 / Troubleshooting](#故障排除--troubleshooting)
6. [最佳实践 / Best Practices](#最佳实践--best-practices)

## 快速开始 / Quick Start

### 首次使用 / First Time Use

1. **启动程序** / **Start Program**：
   ```bash
   python main.py
   ```

2. **基本配置** / **Basic Configuration**：
   - 点击"设置"按钮 / Click "Settings" button
   - 配置IAR安装路径 / Configure IAR installation path
   - 设置项目路径 / Set project path
   - 选择编译配置（支持多配置项目）/ Select build configuration (supports multi-configuration projects)
   - 配置bin起始地址 / Configure bin start address
   - 选择配置文件 / Select configuration file

3. **开始编译** / **Start Compilation**：
   - 点击"开始编译"按钮 / Click "Start Compilation" button
   - 输入更新信息 / Input update information
   - 等待编译完成 / Wait for compilation to complete

4. **一键执行** / **One-Click Execution**：
   - 点击"一键执行"按钮 / Click "One-Click Execution" button
   - 自动完成Git检查、版本检查、编译、文件处理等全流程 / Automatically complete Git check, version check, compilation, file processing workflow
   - 无需手动干预，全流程自动化 / No manual intervention required, fully automated workflow

## 详细配置 / Detailed Configuration

### 项目设置 / Project Settings

#### IAR安装路径 / IAR Installation Path
- **作用** / **Purpose**：指定IAR Embedded Workbench的安装目录
- **格式** / **Format**：绝对路径，如 `C:/Program Files (x86)/IAR Systems/Embedded Workbench 8.3`
- **要求** / **Requirements**：路径必须包含IAR编译器可执行文件

#### 项目路径 / Project Path
- **作用** / **Purpose**：指定IAR项目的根目录（不是.ewp文件路径）
- **格式** / **Format**：绝对路径或相对路径
- **要求** / **Requirements**：目录必须包含EWARM子目录和.ewp项目文件
- **示例** / **Example**：`E:/MCU_Program/SW_ESC_Gimbal`（包含EWARM/MCU.ewp）

#### IAR项目文件路径 / IAR Project File Path
- **作用** / **Purpose**：指定具体的.ewp文件路径
- **格式** / **Format**：绝对路径或相对路径
- **要求** / **Requirements**：必须是有效的.ewp文件
- **示例** / **Example**：`E:/MCU_Program/SW_ESC_Gimbal/EWARM/MCU.ewp`

#### 本地发布目录 / Local Publish Directory
- **作用** / **Purpose**：固件文件的本地发布目录
- **默认值** / **Default**：项目目录下的`fw_publish`文件夹
- **特点** / **Features**：自动创建，排除在Git版本控制之外

#### 远程发布目录 / Remote Publish Directory
- **作用** / **Purpose**：可选的远程固件发布目录
- **格式** / **Format**：绝对路径
- **特点** / **Features**：按`项目名_分支名`创建子目录
- **开关** / **Switch**：可启用/禁用此功能

### 二进制设置 / Binary Settings

#### bin起始地址 / Bin Start Address
- **作用** / **Purpose**：固件在Flash中的起始地址
- **格式** / **Format**：十六进制，如 `0x8000000`
- **用途** / **Usage**：用于二进制文件修改时的地址计算

#### 配置文件 / Configuration File
- **作用** / **Purpose**：包含版本号定义的文件
- **格式** / **Format**：C源文件，如 `main.c`
- **要求** / **Requirements**：必须包含版本号定义宏

## 功能详解 / Feature Details

### 版本管理 / Version Management

#### 固件版本 / Firmware Version
- **格式** / **Format**：`V主版本.次版本.修订版本.构建版本`
- **示例** / **Example**：`V1.0.0.1` → `V1.0.0.2`
- **递增规则** / **Increment Rules**：每次编译自动递增构建版本号

#### 工具版本 / Tool Version
- **格式** / **Format**：`主版本.次版本.修订版本.构建版本`
- **示例** / **Example**：`1.0.2.1`
- **递增规则** / **Increment Rules**：仅在打包exe时递增

### Git集成 / Git Integration

#### 自动提交 / Automatic Commit
- **触发时机** / **Trigger**：每次编译时自动执行
- **提交内容** / **Commit Content**：
  - 版本号更新
  - 配置文件修改
  - Release Notes更新

#### 提交信息 / Commit Message
- **格式** / **Format**：`发布{版本号}版本 - {用户输入信息}`
- **示例** / **Example**：`发布V1.0.0.2版本 - 修复了LED闪烁问题`
- **输入方式** / **Input Method**：弹出对话框，支持多行输入

### 二进制文件修改 / Binary File Modification

#### 注入信息 / Injected Information
- **Git Commit ID**：当前Git提交的短哈希值（7字符十六进制字符串）
- **文件大小** / **File Size**：bin文件的实际字节大小（32位无符号整数，小端序）
- **CRC校验值** / **CRC Checksum**：整个bin文件的CRC32校验值（32位无符号整数，小端序）
- **哈希校验值** / **Hash Checksum**：32字节的哈希校验值（包含magic number和填充）

**注意** / **Note**：固件版本号通过修改源文件后重新编译来更新，不直接修改bin文件。

#### 修改位置 / Modification Locations
- **Commit ID地址** / **Commit ID Address**：通过`#pragma location`在C代码中指定的内存地址
- **文件大小地址** / **File Size Address**：Commit ID地址 + 7字节偏移
- **CRC校验地址** / **CRC Address**：文件大小地址 + 4字节偏移
- **哈希校验地址** / **Hash Address**：通过`#pragma location`在C代码中指定的内存地址

#### 数据格式说明 / Data Format Description
- **Commit ID格式** / **Commit ID Format**：7字符十六进制字符串，如"a1b2c3d"
- **文件大小格式** / **File Size Format**：4字节小端序32位无符号整数
- **CRC格式** / **CRC Format**：4字节小端序32位无符号整数
- **哈希格式** / **Hash Format**：32字节数组，前4字节为magic number (0x12345678)，后28字节为填充

#### 内存布局示例 / Memory Layout Example
```
地址偏移    内容          大小      说明
0x00       "a1b2c3d"     7字节     Git Commit ID（短哈希）
0x07       0x12345678    4字节     文件大小（小端序）
0x0B       0xABCDEF01    4字节     CRC32校验值（小端序）
0x0F       0x12345678    4字节     哈希校验值（magic number）
0x13       0x00000000    28字节    哈希校验值（填充）
```

### Release Notes管理 / Release Notes Management

#### 自动生成 / Automatic Generation
- **文件位置** / **File Location**：项目根目录的`RELEASE_NOTES.md`
- **更新时机** / **Update Trigger**：每次编译时自动更新
- **内容格式** / **Content Format**：Markdown格式

#### 内容结构 / Content Structure
```markdown
# 发布说明 / Release Notes

## 版本 {版本号} / Version {version}
- 发布日期 / Release Date: {日期}
- 分支 / Branch: {分支名}
- 提交 / Commit: {commit_id}

### 更新内容 / Updates
{用户输入的更新信息，自动换行处理}
```

### 文件发布管理 / File Publishing Management

#### 本地发布 / Local Publishing
- **发布目录** / **Publish Directory**：项目目录下的`fw_publish`文件夹
- **文件类型** / **File Types**：.bin文件（必需），.out文件（可选）
- **命名规则** / **Naming Convention**：`项目名_v版本号_commitID.bin/.out`

#### 文件名时间戳 / Filename Timestamp
- **功能** / **Function**：可选择在文件名中添加时间戳
- **格式** / **Format**：`项目名_v版本号_commitID_YYYYMMDD_HHMMSS.bin`
- **默认状态** / **Default State**：不添加时间戳
- **配置位置** / **Configuration Location**：设置页面勾选框

#### .out文件发布 / .out File Publishing
- **功能** / **Function**：可选择同时发布.out文件
- **文件来源** / **File Source**：自动查找与.bin文件同名的.out文件
- **命名规则** / **Naming Convention**：与.bin文件使用相同的命名规则
- **默认状态** / **Default State**：不发布.out文件
- **配置位置** / **Configuration Location**：设置页面勾选框

#### 发布流程 / Publishing Process
1. **编译完成** / **Compilation Complete**：IAR编译成功后
2. **bin文件查找** / **Bin File Finding**：严格匹配.ewp文件名对应的.bin文件
3. **文件复制** / **File Copying**：复制.bin文件到发布目录
4. **可选复制** / **Optional Copying**：如果启用，复制.out文件
5. **远程发布** / **Remote Publishing**：如果启用，复制到远程目录

#### bin文件查找策略 / Bin File Finding Strategy
- **严格匹配** / **Strict Matching**：只查找与.ewp文件名完全一致的.bin文件
- **查找位置** / **Search Location**：`{项目根目录}/EWARM/Debug/Exe/`
- **命名规则** / **Naming Rule**：`{项目名}.bin`（如MCU.ewp → MCU.bin）
- **错误处理** / **Error Handling**：如果找不到匹配文件，直接报错，不选择其他文件

## 高级功能 / Advanced Features

### 远程发布 / Remote Publishing

#### 配置方法 / Configuration Method
1. 在设置中启用远程发布开关 / Enable remote publish switch in settings
2. 设置远程发布目录（绝对路径）/ Set remote publish directory (absolute path)
3. 保存配置 / Save configuration

#### 目录结构 / Directory Structure
```
远程发布目录/
├── 项目名_分支名1/
│   ├── 固件文件_v版本号_commit.bin
│   ├── 固件文件_v版本号_commit.out (可选)
│   └── RELEASE_NOTES.md
└── 项目名_分支名2/
    ├── 固件文件_v版本号_commit.bin
    ├── 固件文件_v版本号_commit.out (可选)
    └── RELEASE_NOTES.md
```

### 可执行文件打包 / Executable Packaging

#### 打包命令 / Packaging Command
```bash
python build_exe.py
```

#### 输出文件 / Output Files
- **Spec文件** / **Spec File**：`IAR_Firmware_Publish_Tool.spec`
- **可执行文件** / **Executable**：`IAR_Firmware_Publish_Tool_v{版本号}.exe`
- **输出目录** / **Output Directory**：`release/`

#### 自动功能 / Automatic Features
- 工具版本号自动递增 / Automatic tool version increment
- 依赖项自动打包 / Automatic dependency packaging
- 配置文件自动复制 / Automatic configuration file copying

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

#### 1. 配置不完整 / Configuration Incomplete
**症状** / **Symptoms**：提示"配置不完整" / Prompt "Configuration incomplete"

**解决方案** / **Solutions**：
- 检查IAR安装路径是否正确 / Check if IAR installation path is correct
- 确认项目路径包含.ewp文件 / Confirm project path contains .ewp files
- 验证bin起始地址格式 / Verify bin start address format
- 确认配置文件存在 / Confirm configuration file exists

#### 2. 编译失败 / Compilation Failed
**症状** / **Symptoms**：IAR编译过程出错 / IAR compilation process error

**常见错误** / **Common Errors**：
- `ERROR, Failed to open project file: Illegal path` - 路径格式错误
- `编译成功但未找到输出bin文件` - bin文件查找失败
- `配置不完整` - 配置文件路径问题

**解决方案** / **Solutions**：
- 检查IAR是否正确安装 / Check if IAR is properly installed
- 验证项目路径和文件 / Verify project path and files
- 确认IAR版本兼容性 / Confirm IAR version compatibility
- 检查项目配置 / Check project configuration
- 确保项目路径指向包含.ewp文件的目录 / Ensure project path points to directory containing .ewp files
- 检查bin文件是否与ewp文件名一致 / Check if bin file name matches .ewp file name

#### 3. Git操作失败 / Git Operation Failed
**症状** / **Symptoms**：Git提交或状态检查失败 / Git commit or status check failed

**解决方案** / **Solutions**：
- 确认项目是Git仓库 / Confirm project is a Git repository
- 检查Git配置 / Check Git configuration
- 验证网络连接 / Verify network connection
- 检查文件权限 / Check file permissions

#### 4. 路径和文件查找问题 / Path and File Finding Issues
**症状** / **Symptoms**：bin文件查找失败或路径错误 / Bin file finding failed or path errors

**常见问题** / **Common Issues**：
- 备份了错误的bin文件（如mcu_old.bin、MCU123333_backup.bin等）/ Backed up wrong bin files (e.g., mcu_old.bin, MCU123333_backup.bin, etc.)
- 提示"编译成功但未找到输出bin文件" / Prompt "Compilation successful but no output bin file found"
- IAR编译报错"Illegal path" / IAR compilation error "Illegal path"

**解决方案** / **Solutions**：
- 确保项目路径指向项目根目录，不是.ewp文件路径 / Ensure project path points to project root directory, not .ewp file path
- 检查EWARM/Debug/Exe目录下是否存在与.ewp文件名一致的.bin文件 / Check if .bin file with same name as .ewp file exists in EWARM/Debug/Exe directory
- 确认.ewp文件路径配置正确 / Confirm .ewp file path configuration is correct
- 检查IAR编译输出目录结构 / Check IAR compilation output directory structure
- 查看日志文件获取详细错误信息 / Check log files for detailed error information

#### 5. 远程发布失败 / Remote Publishing Failed
**症状** / **Symptoms**：文件未复制到远程目录 / Files not copied to remote directory

**解决方案** / **Solutions**：
- 检查远程目录路径是否正确 / Check if remote directory path is correct
- 确认目录权限 / Confirm directory permissions
- 验证远程发布开关状态 / Verify remote publish switch status
- 检查磁盘空间 / Check disk space

### 日志文件 / Log Files

#### 日志位置 / Log Location
- **路径** / **Path**：`logs/build_YYYYMMDD.log`
- **内容** / **Content**：详细的编译和操作日志
- **用途** / **Purpose**：故障诊断和问题追踪

#### 日志级别 / Log Levels
- **INFO**：一般信息 / General information
- **WARNING**：警告信息 / Warning messages
- **ERROR**：错误信息 / Error messages
- **DEBUG**：调试信息 / Debug information

## 最佳实践 / Best Practices

### 项目组织 / Project Organization

#### 目录结构 / Directory Structure
```
项目根目录/
├── src/                    # 源代码目录
├── fw_publish/            # 本地发布目录
├── RELEASE_NOTES.md       # 发布说明
├── .gitignore             # Git忽略文件
└── 其他项目文件...
```

#### Git工作流 / Git Workflow
1. **开发分支** / **Development Branch**：用于日常开发
2. **发布分支** / **Release Branch**：用于稳定版本发布
3. **版本标签** / **Version Tags**：标记重要版本

### 版本管理策略 / Version Management Strategy

#### 固件版本 / Firmware Version
- **主版本** / **Major**：重大功能更新
- **次版本** / **Minor**：新功能添加
- **修订版本** / **Revision**：bug修复
- **构建版本** / **Build**：每次编译递增

#### 工具版本 / Tool Version
- **递增时机** / **Increment Timing**：仅在打包exe时
- **版本格式** / **Version Format**：单数字版本部分（0-9）
- **重置规则** / **Reset Rules**：主版本超过9时重置为1

### 配置管理 / Configuration Management

#### 配置文件优先级 / Configuration File Priority
1. `user_config.json` - 用户配置（最高优先级）
2. `config.json` - 默认配置（最低优先级）

#### 配置备份 / Configuration Backup
- 定期备份`user_config.json`
- 使用版本控制管理配置变更
- 保留配置历史记录

### 发布流程 / Release Process

#### 标准发布流程 / Standard Release Process
1. **代码开发** / **Code Development**：在开发分支进行
2. **功能测试** / **Feature Testing**：验证新功能
3. **版本准备** / **Version Preparation**：更新版本号
4. **编译发布** / **Compile and Release**：使用工具编译
5. **质量检查** / **Quality Check**：验证发布文件
6. **部署分发** / **Deploy and Distribute**：分发给用户

#### 紧急发布流程 / Emergency Release Process
1. **问题识别** / **Problem Identification**：快速定位问题
2. **修复开发** / **Fix Development**：紧急修复
3. **快速测试** / **Quick Testing**：最小化测试
4. **立即发布** / **Immediate Release**：快速发布修复版本

---

## 多语言支持 / Multi-language Support

### 支持语言 / Supported Languages
- **简体中文** / **Simplified Chinese** (zh_CN)
- **繁体中文** / **Traditional Chinese** (zh_TW)
- **English** (en_US)

### 切换方法 / Switch Method
1. 点击设置按钮 / Click Settings button
2. 选择语言选项 / Select language option
3. 点击保存 / Click Save

## 联系支持 / Contact Support

如果您在使用过程中遇到问题，请：

If you encounter problems during use, please:

1. **查看日志文件** / **Check Log Files**：`logs/build_YYYYMMDD.log`
2. **查看常见问题** / **Check FAQ**：参考本文档故障排除部分
3. **提交Issue** / **Submit Issue**：在GitHub上创建Issue
4. **联系开发者** / **Contact Developer**：通过GitHub联系

---

*最后更新 / Last Updated: 2025-01-13 (v1.0.4.2)*
