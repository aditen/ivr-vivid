import {NextPage} from "next";
import {
    AppBar,
    Button,
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
import {Autocomplete} from "@material-ui/lab";
import {YoloClassImages, YoloClassName, YoloTypesAsArray} from "../src/YoloClassName";
import {LocatedObject} from "../src/LocatedObject";

const demoImages = Array.from(Array(32).keys()).map(x => x + 1)
    .map(num => "https://iten.engineering/files/keyframes/00032/shot00032_" + num + "_RKF.png");

const MainPage: NextPage = () => {

    const [figures, setFigures] = useState<LocatedObject[]>([]);
    const [typeToAdd, setTypeToAdd] = useState<YoloClassName | null>(null);
    const [querySubmitted, setQuerySubmitted] = useState<boolean>(false);

    const isLargeScreen = useMediaQuery('(min-width:670px)');

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
                    <Button variant={"contained"} color={"secondary"} onClick={() => {
                        setFigures([]);
                    }}><Icon>delete</Icon>Clear canvas</Button>
                </div>
                <Button variant={"contained"} color={"default"} disabled={figures.length == 0}
                        onClick={() => setQuerySubmitted(true)}><Icon>done</Icon>Submit query</Button>
            </Grid>
        </Grid>
        <Dialog open={querySubmitted} fullScreen={true}
                onClose={() => setQuerySubmitted(false)}>
            <DialogContent>
                <GridList cellHeight={120} cols={6}>
                    {demoImages.map((tile) => (
                        <GridListTile key={tile} cols={1}>
                            <img src={tile}/>
                        </GridListTile>
                    ))}
                </GridList>
                {JSON.stringify(figures)}
            </DialogContent>
        </Dialog>
    </React.Fragment>)
};

export default MainPage;
