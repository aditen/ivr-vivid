import {NextPage} from "next";
import {
    AppBar,
    Button,
    Card,
    CardActions,
    CardContent,
    Chip,
    CircularProgress,
    Dialog,
    DialogContent,
    Grid,
    GridList,
    GridListTile,
    GridListTileBar,
    Icon,
    IconButton,
    TextField,
    Toolbar,
    Typography,
    useMediaQuery
} from "@material-ui/core";
import * as React from "react";
import {useEffect, useState} from "react";
import Head from "next/dist/next-server/lib/head";
import {Rnd} from "react-rnd";
import {Autocomplete} from "@material-ui/lab";
import {YoloClassImages, YoloClassName, YoloTypesAsArray} from "../src/YoloClassName";
import axios from "axios";
import {FilterCriteria} from "../src/FilterCriteria";

const MainPage: NextPage = () => {
    const [typeToAdd, setTypeToAdd] = useState<YoloClassName | null>(null);
    const [classSuggestions, setClassSuggestions] = useState<string[]>([]);
    const [resultMatrix, setResultMatrix] = useState<string[][]>([[]]);
    const [apiStatus, setApiStatus] = useState<'loading' | 'error' | 'online'>("loading");
    const [queryStatus, setQueryStatus] = useState<'defining' | 'loading' | 'result' | 'error'>();
    const isLargeScreen = useMediaQuery('(min-width:670px)');
    const [filterCriteria, setFilterCriteria] = useState<FilterCriteria>({
        locatedObjects: [],
        classNames: [],
        gridWidth: isLargeScreen ? 8 : 4,
        text: ""
    });

    useEffect(() => setFilterCriteria({...filterCriteria, gridWidth: isLargeScreen ? 8 : 4}), [isLargeScreen]);

    const checkApiStatus = async () => {
        try {
            await axios.get<any>("http://localhost:5000/");
            setApiStatus("online");
        } catch (e) {
            setApiStatus("error");
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
            const res = await axios.post<string[][]>("http://localhost:5000/execute_query", {
                ...filterCriteria,
                text: !!filterCriteria.text ? filterCriteria.text : null
            });
            setResultMatrix(res.data);
            setQueryStatus("result");
        } catch (e) {
            console.error(e);
            setQueryStatus("error");
            alert("Error! Please reload page! If you see this again, contact the admin.");
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
                                                                                  fig.width = Number.parseFloat(ref.style.width.replace("px", ""));
                                                                                  fig.height = Number.parseFloat(ref.style.height.replace("px", ""));
                                                                              }}
                                                                              style={{
                                                                                  borderColor: "black",
                                                                                  borderWidth: "medium",
                                                                                  borderStyle: "dotted"
                                                                              }}>
                            <img draggable={false} style={{width: "100%", height: "100%"}}
                                 src={!!YoloClassImages[fig.className] ? YoloClassImages[fig.className] : "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Question_mark_%28black%29.svg/200px-Question_mark_%28black%29.svg.png"}/>
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
                                options={YoloTypesAsArray}
                                fullWidth={true}
                                renderInput={(params) => <TextField {...params} label="Choose object..."
                                                                    variant="outlined"/>}
                            />
                            <IconButton disabled={!typeToAdd} style={{marginLeft: 10}} onClick={() => {
                                setFilterCriteria({
                                    ...filterCriteria, locatedObjects: [...filterCriteria.locatedObjects, {
                                        className: typeToAdd,
                                        height: 100,
                                        width: 100,
                                        xOffset: isLargeScreen ? 270 : 122,
                                        yOffset: isLargeScreen ? 130 : 35
                                    }]
                                })
                            }}><Icon>add</Icon></IconButton>
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
                                options={classSuggestions}
                                fullWidth={true}
                                renderInput={(params) => <TextField {...params} label="Choose potential image class..."
                                                                    variant="outlined"/>}
                            />
                        </div>
                        <div>
                            {filterCriteria.classNames.map((cls, clsIdx) => <Chip variant={"outlined"}
                                                                                  style={{margin: 5}}
                                                                                  key={clsIdx}
                                                                                  label={cls}
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
                        <CardActions>
                            <Button variant={"contained"} color={"primary"}
                                    disabled={filterCriteria.locatedObjects.length == 0 && filterCriteria.classNames.length == 0 && !filterCriteria.text}
                                    onClick={() => executeQuery()}><Icon>done</Icon>Submit</Button>
                            <Button variant={"contained"} color={"secondary"} onClick={() => {
                                setFilterCriteria({
                                    locatedObjects: [],
                                    classNames: [],
                                    gridWidth: filterCriteria.gridWidth,
                                    text: ""
                                });
                                setClassSuggestions([]);
                            }}><Icon>delete</Icon>Clear</Button>
                        </CardActions>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
        <Dialog open={queryStatus === "result" || queryStatus === "loading"} fullScreen={true}
                onClose={() => setQueryStatus("defining")}>
            <AppBar position={"static"} style={{marginBottom: 10}}>
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
                    {resultMatrix.map(matRow => matRow.filter(item => !!item).map(item => <GridListTile key={item}
                                                                                                        cols={1}>
                        <img style={{width: "100%", height: "auto"}} src={item}/>
                        <GridListTileBar title={"00032"} actionIcon={
                            <IconButton style={{color: "white"}} onClick={() => alert("okay, submitted!")}>
                                <Icon>check</Icon>
                            </IconButton>
                        }/>
                    </GridListTile>))}
                </GridList>}
            </DialogContent>
        </Dialog>
    </React.Fragment>)
};

export default MainPage;
