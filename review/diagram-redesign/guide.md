# HTML 幻灯片图解编辑契约
权威来源 /Users/sunzy/big-data/docs/textbook/chapters/*.tex；现有数据 /private/tmp/bdm-slide-visuals/original.json。只输出所负责章节到 temp JSON，不修改网站。根代理实现下述图解组件，所有展示字符串可用 **加粗** 与行内 TeX \\( ... \\)。

目标：每讲选择约 10–16 个教学价值高的页面，创建真实图解（精确图表、结构图、时间窗口、推导关系），替换纯文字列表/表格。不要为凑数加装饰。保留定义、假设、符号释义、推导解释、算例条件、结果、边界及 detailRef。可把原 workedExample 的完整计算放入图解节点、body 或 equation；避免两套重复计算。已有403页页序保持，可增页但须明确说明。图解页优先 split（左右），右图区约 535×350px；图中文字标题18–20px，节点详细17px。body 应2段共约160–220汉字以内，超长公式拆步骤。图解不是提纲。

每个 slide 可新增 diagram 对象，必须有 type,title,description,encoding,note（可空）。description 为完整无障碍文字解释，encoding 说明“模型结构示意”“教材算例 · 同一比例尺”等； note 在图下可见，须精炼且解释关键关系。为布局选 slide.layout='split',density='compact'。新 diagram 通常替换已有 visual 或 workedExample，但不要删必要信息。至少十余页/讲有图，尤其推导、案例，不能全是同款框箭头。

支持六种 schema:
1 graph: {type:'graph',title,description,encoding,note,nodes:[{id,x,y,w,h,label,detail,tone,shape}],edges:[{from,to,label,dashed,via:[{x,y}],labelX,labelY}]}
 坐标与框宽高均0..100百分比，画布物理比例1.6(约535×334)。默认w26,h20,shape'rect',tone'blue'; tone支持blue,teal,muted,rose；circle用于Petri。边从框边界起止，箭头到目标外边界；可用via设置回路避开框。标签坐标可选，不宜>12汉字。默认3列 x17,50,83；2行 y27,75，框w27 h24。详细文字每框约20汉字以下，可含短数学。节点label+detail不能超过3行。最多6–8框。
2 bars: {type:'bars',title,description,encoding,note,domain:[min,max],unit,rows:[{label,value,detail,tone}],ticks:[number]}
 精确共零点水平条，2–5条；value必须来自已给教材算例。detail短句解释，value数值展示。负收益用负半轴。相同单位。
3 intervals: {type:'intervals',title,description,encoding,note,domain:[min,max],unit,ticks:[number],reference:number,referenceLabel,rows:[{label,low,high,estimate,detail,tone}]}
 精确置信区间/识别上下界共轴，最多3组；reference可以0/业务阈值，数字都必须有来源。
4 matrix: {type:'matrix',title,description,encoding,note,columns:[string],rowLabels:[string],cells:[[{text,detail,value,tone}]],scale:[min,max]}
 2×2 或2×3，text可为公式,detail约14字内,value可选只用于精确数值色深。须说明行列语义。matrix不是长表。
5 timeline: {type:'timeline',title,description,encoding,note,domain:[min,max],unit,ticks:[number],rows:[{label,segments:[{start,end,label,tone}],points:[{at,label,tone}]}],reference:number,referenceLabel}
 最多3行；单位相同，可用相对时点，需要注明“相对时间示意/非实测”。区间表示训练/观察/结果窗或等待/服务真实时间；0刻线可以干预时点。
6 plot: {type:'plot',title,description,encoding,note,xDomain:[min,max],yDomain:[min,max],xLabel,yLabel,xTicks:[number],yTicks:[number],series:[{label,points:[[x,y]],tone,dashed}],markers:[{x,y,label,tone}],regions:[{points:[[x,y]],tone,label}]}
 精确解析曲线或教材已给算例点，禁止捏造实测数据。series折线近似应注“模型曲线”；regions只填精确可行域。最多2条曲线+4标记，label短。

note/description 和 body 应共同确保独立阅读。图中公式统一行内TeX，图例单位和编码明确。禁止用文本希腊字母/下标等替代TeX。纯结构图是示意，数量不由面积推断；数据图坐标必须真按数值。算法代码只保留原有。

额外输出 figure-notes Markdown：逐个新增图列chapter/page,title,教学问题,出处（tex节/现有算例）,类型,精确或示意,核验计算。指出内容风险，不夸称所有内容已审核。
