import {NextPage} from "next";
import {
    AppBar,
    Button, Chip,
    Dialog,
    DialogContent,
    Grid,
    GridList,
    GridListTile,
    Icon,
    IconButton,
    TextField,
    Toolbar,
    Typography,
    useMediaQuery
} from "@material-ui/core";
import * as React from "react";
import {useState} from "react";
import Head from "next/dist/next-server/lib/head";
import {Rnd} from "react-rnd";
import {Autocomplete, FilterOptionsState} from "@material-ui/lab";
import {YoloClassImages, YoloClassName, YoloTypesAsArray} from "../src/YoloClassName";
import {LocatedObject} from "../src/LocatedObject";
import axios from "axios";

const MainPage: NextPage = () => {

    const [figures, setFigures] = useState<LocatedObject[]>([]);
    const [typeToAdd, setTypeToAdd] = useState<YoloClassName | null>(null);
    const [querySubmitted, setQuerySubmitted] = useState<boolean>(false);
    const [classSuggestions, setClassSuggestions] = useState<string[]>([]);
    const [selectedClasses, setSelectedClasses] = useState<string[]>([]);
    const [searchText, setSearchText] = useState<string | undefined>();
    const [resultMatrix, setResultMatrix] = useState<string[][]>([[]]);

    const fetchClassSuggestions = async (query: string) => {
        try {
            const res = await axios.get<string[]>("http://localhost:5000/suggest_imagenet_class?query=" + query);
            console.log(res.data);
            setClassSuggestions(res.data);
        } catch (e) {
            console.error(e);
            alert("Error! Please reload page! If you see this again, contact the admin.");
        }
    };

    const isLargeScreen = useMediaQuery('(min-width:670px)');

    const executeQuery = async () => {
        try {
            const res = await axios.post<string[][]>("http://localhost:5000/execute_query", {
                locatedObjects: figures,
                classNames: selectedClasses,
                gridWidth: isLargeScreen ? 8 : 4
            });
            setResultMatrix(res.data);
            console.log(res.data);
        } catch (e) {
            console.error(e);
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
                <Typography variant={"h4"}>
                    ViViD</Typography>
            </Toolbar>
        </AppBar>
        <Grid justify={"space-evenly"} container={true}>
            <Grid item={true} component={"div"} style={{padding: 5}}>
                <div style={{
                    width: isLargeScreen ? '640px' : '344px',
                    height: isLargeScreen ? '360px' : '171px',
                    borderColor: "black",
                    borderWidth: "medium",
                    borderStyle: "solid"
                }}>
                    {figures.map((fig, idx) => <Rnd key={idx} bounds={"parent"}
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
            </Grid>
            <Grid item={true} component={"div"} xs={12} md={4} style={{padding: 5}}>
                <div style={{display: "flex"}}>
                    <Autocomplete
                        onChange={(event, newValue) => {
                            setTypeToAdd(newValue as YoloClassName);
                        }}
                        options={YoloTypesAsArray}
                        fullWidth={true}
                        renderInput={(params) => <TextField {...params} label="Choose object..." variant="outlined"/>}
                    />
                    <IconButton disabled={!typeToAdd} style={{marginLeft: 10}} onClick={() => {
                        setFigures([...figures, {
                            className: typeToAdd,
                            height: 100,
                            width: 100,
                            xOffset: isLargeScreen ? 270 : 122,
                            yOffset: isLargeScreen ? 130 : 35
                        }])
                    }}><Icon>add</Icon></IconButton>
                </div>
                <div style={{marginTop: 15, marginBottom: 15}}>
                    <Autocomplete
                        onInputChange={(event, newValue) => {
                            fetchClassSuggestions(newValue).catch(console.error);
                        }}
                        onChange={(event, value) => {
                            if (!!value) {
                                selectedClasses.push(value);
                                setSelectedClasses([...selectedClasses]);
                            }
                        }}
                        filterOptions={(options: string[], state: FilterOptionsState<string>) => {
                            return options;
                        }}
                        options={classSuggestions}
                        fullWidth={true}
                        renderInput={(params) => <TextField {...params} label="Choose potential image class..."
                                                            variant="outlined"/>}
                    />
                </div>
                <div>
                    {selectedClasses.map((cls, clsIdx) => <Chip variant={"outlined"}
                                                                style={{margin: 5}}
                                                                key={clsIdx}
                                                                label={cls}
                                                                onDelete={() => {
                                                                    selectedClasses.splice(clsIdx, 1);
                                                                    setSelectedClasses([...selectedClasses]);
                                                                }}
                    />)}
                </div>
                <div>
                    <TextField fullWidth={true} label="Enter video text" variant="outlined"/>
                </div>
                <div style={{marginTop: 15, marginBottom: 15}}>
                    <Button variant={"contained"} color={"secondary"} onClick={() => {
                        setFigures([]);
                        setSelectedClasses([]);
                    }}><Icon>delete</Icon>Clear Query</Button>
                </div>
                <div>
                    <Button variant={"contained"} color={"default"} disabled={figures.length == 0}
                            onClick={() => executeQuery() && setQuerySubmitted(true)}><Icon>done</Icon>Submit
                        query</Button>
                </div>
            </Grid>
        </Grid>
        <Dialog open={querySubmitted} fullScreen={true}
                onClose={() => setQuerySubmitted(false)}>
            <DialogContent>
                <GridList cellHeight={"auto"} cols={!!resultMatrix.length ? resultMatrix[0].length : 0}>
                    {resultMatrix.map(matRow => matRow.filter(item => !!item).map(item => <GridListTile key={item} cols={1}>
                        <img style={{width: "100%", height: "auto"}} src={item}/>
                    </GridListTile>))}
                </GridList>
                {JSON.stringify(figures)}
            </DialogContent>
        </Dialog>
    </React.Fragment>)
};

export default MainPage;
