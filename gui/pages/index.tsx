import {NextPage} from "next";
import {
    AppBar,
    Button,
    ButtonGroup,
    Card,
    CardActions,
    CardContent,
    Chip,
    CircularProgress,
    Dialog,
    DialogContent,
    DialogTitle,
    Grid,
    GridList,
    GridListTile,
    GridListTileBar,
    Icon,
    IconButton,
    Slider,
    TextField,
    Toolbar,
    Typography,
    useMediaQuery
} from "@material-ui/core";
import * as React from "react";
import {useEffect, useState} from "react";
import Head from "next/dist/next-server/lib/head";
import {Rnd} from "react-rnd";
import {
    Autocomplete,
    Timeline,
    TimelineConnector,
    TimelineContent,
    TimelineDot,
    TimelineItem,
    TimelineSeparator
} from "@material-ui/lab";
import {YoloClassName, YoloTypesAsArray} from "../src/YoloClassName";
import axios from "axios";
import {FilterCriteria} from "../src/FilterCriteria";
import {VividKeyframe} from "../src/VividKeyframe";
import {KeyframeUtils} from "../src/KeyframeUtils";
import {RandomVideo} from "../src/RandomVideo";

const quantityMarks = [
    {
        value: 1,
        label: '1',
    },
    {
        value: 5,
        label: '5',
    },
    {
        value: 10,
        label: '10',
    },
    {
        value: 15,
        label: '15+',
    }
];

const MainPage: NextPage = () => {
    const [typeToAdd, setTypeToAdd] = useState<YoloClassName | null>(null);
    const [classSuggestions, setClassSuggestions] = useState<string[]>([]);
    const [resultMatrix, setResultMatrix] = useState<VividKeyframe[][]>([[]]);
    const [keyframeToDisplay, setKeyframeToDisplay] = useState<VividKeyframe | undefined>();
    const [apiStatus, setApiStatus] = useState<'loading' | 'error' | 'online'>("loading");
    const [queryStatus, setQueryStatus] = useState<'defining' | 'loading' | 'result' | 'error'>();
    const isLargeScreen = useMediaQuery('(min-width:670px)');
    const [filterCriteria, setFilterCriteria] = useState<FilterCriteria>({
        locatedObjects: [],
        quantities: [],
        classNames: [],
        gridWidth: isLargeScreen ? 8 : 4,
        text: ""
    });
    const [visualKnownItemVideo, setVisualKnownItemVideo] = useState<RandomVideo | undefined>();
    const [watchingKnownVideo, setWatchingKnownVideo] = useState<boolean>(false);
    const [detectionType, setDetectionType] = useState<'zero' | 'one' | 'range'>("one");
    const [quantityRange, setQuantityRange] = useState<number[]>([1, 15]);

    useEffect(() => setFilterCriteria({...filterCriteria, gridWidth: isLargeScreen ? 8 : 4}), [isLargeScreen]);

    const checkApiStatus = async () => {
        try {
            await axios.get<any>("http://localhost:5000/");
            setApiStatus("online");
        } catch (e) {
            setApiStatus("error");
        }
    };

    const loadVisualKnownItemVideo = async () => {
        try {
            const randomVideo = await axios.get<RandomVideo>("http://localhost:5000/random_visual_known_item");
            setVisualKnownItemVideo(randomVideo.data);
            setWatchingKnownVideo(true);
        } catch (e) {
            setApiStatus("error");
        }
    };

    const submit = (kf: VividKeyframe) => {
        if (!!visualKnownItemVideo) {
            if (kf.video === visualKnownItemVideo.id) {
                alert("Congrats! Correct vide found!");
            } else {
                alert("Sorry! that was wrong...")
            }
        } else {
            alert("will be implemented!");
        }
    };

    useEffect(() => {
        checkApiStatus().catch(console.error);
    }, []);

    const fetchClassSuggestions = async (query: string) => {
        try {
            const res = await axios.get<string[]>("http://localhost:5000/suggest_imagenet_class?query=" + query);
            setClassSuggestions(res.data);
        } catch (e) {
            console.error(e);
            alert("Error! Please reload page! If you see this again, contact the admin.");
        }
    };

    const executeQuery = async () => {
        try {
            setQueryStatus("loading");
            const res = await axios.post<VividKeyframe[][]>("http://localhost:5000/execute_query", {
                ...filterCriteria,
                locatedObjects: filterCriteria.locatedObjects.map(value => {
                    return {
                        xOffset: isLargeScreen ? value.xOffset / 640 : value.xOffset / 344,
                        yOffset: isLargeScreen ? value.yOffset / 360 : value.yOffset / 171,
                        width: isLargeScreen ? value.width / 640 : value.width / 344,
                        height: isLargeScreen ? value.height / 360 : value.height / 171,
                        className: value.className
                    };
                }),
                text: !!filterCriteria.text ? filterCriteria.text : null
            } as FilterCriteria);
            setResultMatrix(res.data);
            setQueryStatus("result");
            setApiStatus("online");
        } catch (e) {
            console.error(e);
            setQueryStatus("error");
            alert("Error! Please reload page! If you see this again, contact the admin.");
        }
    };

    const addYoloObject = () => {
        if (detectionType === "one") {
            setFilterCriteria({
                ...filterCriteria, locatedObjects: [...filterCriteria.locatedObjects, {
                    className: typeToAdd,
                    height: 100,
                    width: 100,
                    xOffset: isLargeScreen ? 270 : 122,
                    yOffset: isLargeScreen ? 130 : 35
                }]
            });
            setQuantityRange([1, 15]);
        } else {
            setFilterCriteria({
                ...filterCriteria,
                quantities: [...filterCriteria.quantities.filter(value => value.className !== typeToAdd), {
                    className: typeToAdd,
                    minQuantity: detectionType === "zero" ? 0 : quantityRange[0],
                    maxQuantity: detectionType === "zero" ? 0 : quantityRange[1]
                }]
            });
            setQuantityRange([1, 15]);
        }
    };

    return (<React.Fragment>
        <Head>
            <title>ViViD</title>
            <link rel="icon" href="https://www.uzh.ch/favicon.ico"/>
            <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"/>
        </Head>
        <AppBar position={"static"} style={{marginBottom: 10}}>
            <Toolbar style={{padding: 5}}>
                <img
                    src={"https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Universit%C3%A4t_Z%C3%BCrich_logo.svg/2000px-Universit%C3%A4t_Z%C3%BCrich_logo.svg.png"}
                    style={{height: 50, width: "auto", marginRight: 10}}/>
                <Typography variant={"h4"} style={{flexGrow: 1}}>
                    ViViD</Typography>
                <IconButton onClick={() => loadVisualKnownItemVideo()}><Icon>play_arrow</Icon></IconButton>
                {apiStatus === "online" && <Icon style={{color: "green", marginRight: 5}}>check</Icon>}
                {apiStatus === "error" && <Icon style={{color: "red", marginRight: 5}}>clear</Icon>}
            </Toolbar>
        </AppBar>
        <Grid justify={"space-evenly"} container={true}>
            <Grid item={true} component={"div"} style={{padding: 5}}>
                <Card>
                    <div style={{
                        width: isLargeScreen ? '640px' : '344px',
                        height: isLargeScreen ? '360px' : '171px',
                        borderColor: "black",
                        borderWidth: "medium",
                        borderStyle: "solid"
                    }}>
                        {filterCriteria.locatedObjects.map((fig, idx) => <Rnd key={idx} bounds={"parent"}
                                                                              default={{
                                                                                  x: fig.xOffset,
                                                                                  y: fig.yOffset,
                                                                                  width: fig.width,
                                                                                  height: fig.height
                                                                              }}
                                                                              onDragStop={(e, d) => {
                                                                                  fig.xOffset = d.x;
                                                                                  fig.yOffset = d.y;
                                                                              }}
                                                                              onResizeStop={(e, direction, ref, delta, position) => {
                                                                                  fig.width = Number.parseFloat(ref.style.width.replaceAll("px", ""));
                                                                                  fig.height = Number.parseFloat(ref.style.height.replaceAll("px", ""));
                                                                              }}
                                                                              style={{
                                                                                  borderColor: "black",
                                                                                  borderWidth: "medium",
                                                                                  borderStyle: "dotted"
                                                                              }}>
                            <img draggable={false} style={{width: "100%", height: "100%"}}
                                 src={"/" + fig.className + ".png"}/>
                        </Rnd>)}

                    </div>
                </Card>
            </Grid>
            <Grid item={true} component={"div"} xs={12} md={4} style={{padding: 5}}>
                <Card>
                    <CardContent>
                        <Typography gutterBottom variant="h4" component="h4">
                            Query
                        </Typography>
                        <div style={{display: "flex"}}>
                            <Autocomplete
                                onChange={(event, newValue) => {
                                    setTypeToAdd(newValue as YoloClassName);
                                }}
                                value={typeToAdd}
                                options={YoloTypesAsArray}
                                fullWidth={true}
                                renderInput={(params) => <TextField {...params} label="Choose object..."
                                                                    variant="outlined"/>}
                            />
                            <ButtonGroup color="primary" style={{marginLeft: 10}}>
                                <Button variant={detectionType === "zero" ? "contained" : "outlined"}
                                        onClick={() => setDetectionType("zero")}>Zero</Button>
                                <Button variant={detectionType === "one" ? "contained" : "outlined"}
                                        onClick={() => setDetectionType("one")}>One</Button>
                                <Button variant={detectionType === "range" ? "contained" : "outlined"}
                                        onClick={() => setDetectionType("range")}>Range</Button>
                            </ButtonGroup>
                            <IconButton disabled={!typeToAdd} onClick={() => {
                                addYoloObject();
                            }}><Icon>add</Icon></IconButton>
                        </div>
                        {detectionType === "range" && <Slider style={{margin: 5}}
                                                              min={1}
                                                              max={15}
                                                              value={quantityRange}
                                                              marks={quantityMarks}
                                                              onChange={(event, value) => setQuantityRange(value as number[])}
                        />}
                        <div>
                            {filterCriteria.quantities.map((cls, clsIdx) => <Chip variant={"outlined"}
                                                                                  style={{
                                                                                      marginTop: 10,
                                                                                      marginRight: 5
                                                                                  }}
                                                                                  key={clsIdx}
                                                                                  label={(cls.minQuantity === 0 && cls.maxQuantity === 0) ? ("no " + cls.className) : cls.maxQuantity === 15 ? (cls.minQuantity + "+ " + cls.className) : (cls.minQuantity + "-" + cls.maxQuantity + " " + cls.className)}
                                                                                  onDelete={() => {
                                                                                      setFilterCriteria({
                                                                                          ...filterCriteria,
                                                                                          quantities: [...filterCriteria.quantities.filter(minQuant => minQuant.className !== cls.className)]
                                                                                      })
                                                                                  }}
                            />)}
                        </div>
                        <div style={{marginTop: 15, marginBottom: 15}}>
                            <Autocomplete
                                onInputChange={(event, newValue) => {
                                    fetchClassSuggestions(newValue).catch(console.error);
                                }}
                                onChange={(event, value) => {
                                    if (!!value) {
                                        setFilterCriteria({
                                            ...filterCriteria,
                                            classNames: [...filterCriteria.classNames, value]
                                        })
                                    }
                                }}
                                filterOptions={(options: string[]) => {
                                    return options.filter(option => filterCriteria.classNames.indexOf(option) === -1);
                                }}
                                renderOption={option => option.replaceAll("_", " ")}
                                options={classSuggestions}
                                fullWidth={true}
                                renderInput={(params) => <TextField {...params} label="Enter image class..."
                                                                    variant="outlined"/>}
                            />
                        </div>
                        <div>
                            {filterCriteria.classNames.map((cls, clsIdx) => <Chip variant={"outlined"}
                                                                                  style={{margin: 5}}
                                                                                  key={clsIdx}
                                                                                  label={cls.replaceAll("_", " ")}
                                                                                  onDelete={() => {
                                                                                      filterCriteria.classNames.splice(clsIdx, 1);
                                                                                      setFilterCriteria({...filterCriteria});
                                                                                  }}
                            />)}
                        </div>
                        <div style={{marginTop: 15, marginBottom: 15}}>
                            <TextField fullWidth={true} label="Enter video text" variant="outlined"
                                       value={filterCriteria.text}
                                       onChange={event => setFilterCriteria({
                                           ...filterCriteria,
                                           text: event.target.value
                                       })}/>
                        </div>
                        <div>
                            <Typography gutterBottom>
                                Grid Width
                            </Typography>
                            <Slider
                                value={filterCriteria.gridWidth}
                                onChange={(event, value) => setFilterCriteria({
                                    ...filterCriteria,
                                    gridWidth: value as number
                                })}
                                valueLabelDisplay="on"
                                step={2}
                                marks
                                min={4}
                                max={12}
                            />
                        </div>
                        <CardActions>
                            <Button variant={"contained"} color={"primary"}
                                    disabled={filterCriteria.locatedObjects.length == 0 && filterCriteria.quantities.length == 0 && filterCriteria.classNames.length == 0 && !filterCriteria.text}
                                    onClick={() => executeQuery()}><Icon>done</Icon>Submit</Button>
                            <Button variant={"contained"} color={"secondary"} onClick={() => {
                                setFilterCriteria({
                                    locatedObjects: [],
                                    quantities: [],
                                    classNames: [],
                                    gridWidth: filterCriteria.gridWidth,
                                    text: ""
                                });
                                setClassSuggestions([]);
                                setDetectionType("one");
                                setQuantityRange([1, 15]);
                                setTypeToAdd(null);
                            }}><Icon>delete</Icon>Clear</Button>
                        </CardActions>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
        <Dialog open={queryStatus === "result" || queryStatus === "loading"} fullScreen={true}
                onClose={() => setQueryStatus("defining")}>
            <AppBar color={"secondary"} position={"static"} style={{marginBottom: 10}}>
                <Toolbar style={{padding: 5}}>
                    <img
                        src={"https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Universit%C3%A4t_Z%C3%BCrich_logo.svg/2000px-Universit%C3%A4t_Z%C3%BCrich_logo.svg.png"}
                        style={{height: 50, width: "auto", marginRight: 10}}/>
                    <Typography variant={"h4"} style={{flexGrow: 1}}>
                        Results</Typography>
                    <IconButton onClick={() => setQueryStatus("defining")}><Icon>close</Icon></IconButton>
                </Toolbar>
            </AppBar>
            <DialogContent>
                {queryStatus === "loading" && <div style={{textAlign: "center"}}><CircularProgress/></div>}
                {queryStatus === "result" &&
                <GridList cellHeight={"auto"} cols={!!resultMatrix.length ? resultMatrix[0].length : 0}>
                    {resultMatrix.map((matRow, idx1) => matRow.map((item, idx2) => <GridListTile
                        key={idx1 + "-" + idx2}
                        cols={1}>
                        {!!item && <><img style={{width: "100%", height: "auto"}} src={KeyframeUtils.getUrl(item)}/>
                            <GridListTileBar titlePosition={"top"} actionIcon={
                                <IconButton style={{color: "white"}} onClick={() => submit(item)}>
                                    <Icon>check</Icon>
                                </IconButton>
                            }/>
                            <GridListTileBar title={item.title} actionIcon={
                                <IconButton style={{color: "white"}} onClick={() => setKeyframeToDisplay(item)}>
                                    <Icon>info</Icon>
                                </IconButton>
                            }/></>}
                        {!item &&
                        <img style={{width: "100%", height: "56.25%"}}
                             src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Solid_white.svg/1024px-Solid_white.svg.png"/>}
                    </GridListTile>))}
                </GridList>}
            </DialogContent>
        </Dialog>
        {!!keyframeToDisplay &&
        <Dialog maxWidth={"md"} fullWidth={true} open={!!keyframeToDisplay}
                onClose={() => setKeyframeToDisplay(undefined)}>
            <DialogTitle>
                {keyframeToDisplay.title}
                <IconButton size={"small"} style={{float: "right"}} onClick={() => setKeyframeToDisplay(undefined)}>
                    <Icon>close</Icon>
                </IconButton></DialogTitle>
            <DialogContent>
                <div style={{textAlign: "center"}}>
                    <iframe
                        src={"https://player.vimeo.com/video/" + keyframeToDisplay.vimeoId + "?autoplay=1#t=" + keyframeToDisplay.atTime}
                        width={isLargeScreen ? 640 : 320} height={isLargeScreen ? 360 : 180}
                        frameBorder="0" allowFullScreen/>
                </div>
                <Typography component={"p"}>{keyframeToDisplay.description}</Typography>
                <>
                    {keyframeToDisplay.tags.map(tag => <Chip style={{margin: 5}} key={tag} label={tag}/>)}
                </>
                <Timeline align="alternate">
                    {KeyframeUtils.getTimelineUrls(keyframeToDisplay).map(kfUrl => <TimelineItem key={kfUrl}>
                        <TimelineSeparator>
                            <TimelineDot/>
                            <TimelineConnector/>
                        </TimelineSeparator>
                        <TimelineContent><img style={{width: "200px", height: "auto"}} src={kfUrl}/></TimelineContent>
                    </TimelineItem>)}
                </Timeline>
            </DialogContent>
        </Dialog>}
        {!!visualKnownItemVideo &&
        <Dialog maxWidth={"md"} open={watchingKnownVideo} onClose={() => setWatchingKnownVideo(false)}>
            <DialogTitle>Find the video!</DialogTitle>
            <DialogContent>
                <div style={{textAlign: "center"}}>
                    <iframe
                        src={"https://player.vimeo.com/video/" + visualKnownItemVideo.vimeoId + "#t=" + visualKnownItemVideo.atTime + "s"}
                        width={isLargeScreen ? 640 : 320} height={isLargeScreen ? 360 : 180}
                        frameBorder="0" allowFullScreen/>
                </div>
            </DialogContent>
        </Dialog>}
    </React.Fragment>)
};

export default MainPage;
